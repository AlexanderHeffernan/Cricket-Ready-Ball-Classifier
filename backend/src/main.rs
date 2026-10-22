use actix_cors::Cors;
use actix_multipart::Multipart;
use actix_web::{http::StatusCode, web, App, HttpRequest, HttpResponse, HttpServer};
use futures_util::StreamExt;
use serde_json::{json, Value};
use std::{
    fs,
    io::Write,
    path::PathBuf,
    sync::Arc,
    time::{Duration, SystemTime},
};
use tempfile::TempDir;
use tokio::{process::Command, sync::Semaphore, time::timeout};

const MAX_IMAGE: usize = 5 * 1024 * 1024;
const MAX_PENDING_BYTES: u64 = 256 * 1024 * 1024;
const MAX_PENDING_FILES: usize = 500;
const RETENTION: Duration = Duration::from_secs(7 * 24 * 3600);

struct State {
    admission: Arc<Semaphore>,
    inference: Arc<Semaphore>,
    storage: Arc<Semaphore>,
    pending: PathBuf,
    python: String,
}

type Failure = (StatusCode, &'static str);
fn bad() -> Failure {
    (StatusCode::BAD_REQUEST, "Invalid image upload")
}
fn unavailable() -> Failure {
    (
        StatusCode::SERVICE_UNAVAILABLE,
        "Service busy; please try again later",
    )
}
fn internal() -> Failure {
    (StatusCode::INTERNAL_SERVER_ERROR, "Image processing failed")
}
fn response(result: Result<Value, Failure>) -> HttpResponse {
    match result {
        Ok(value) => HttpResponse::Ok().json(value),
        Err((code, message)) => HttpResponse::build(code).body(message),
    }
}

// Count every field and byte before copying; no client filename or MIME type is trusted.
async fn parse(
    mut payload: Multipart,
    training: bool,
) -> Result<(Vec<u8>, Option<String>), Failure> {
    let mut image = None;
    let mut label = None;
    let mut fields = 0;
    while let Some(item) = payload.next().await {
        fields += 1;
        if fields > if training { 2 } else { 1 } {
            return Err(bad());
        }
        let mut field = item.map_err(|_| bad())?;
        let name = field.name().unwrap_or("").to_owned();
        let limit = match name.as_str() {
            "image" if image.is_none() => MAX_IMAGE,
            "label" if training && label.is_none() => 15,
            _ => return Err(bad()),
        };
        let mut bytes = Vec::new();
        while let Some(chunk) = field.next().await {
            let chunk = chunk.map_err(|_| bad())?;
            if chunk.len() > limit - bytes.len() {
                return Err((StatusCode::PAYLOAD_TOO_LARGE, "Upload exceeds size limit"));
            }
            bytes.extend_from_slice(&chunk);
        }
        if name == "image" {
            image = Some(bytes);
        } else {
            label = Some(String::from_utf8(bytes).map_err(|_| bad())?);
        }
    }
    let image = image.filter(|b| !b.is_empty()).ok_or_else(bad)?;
    if training && !matches!(label.as_deref(), Some("match_ready" | "not_match_ready")) {
        return Err(bad());
    }
    Ok((image, label))
}

async fn python(
    state: &State,
    args: &[&std::ffi::OsStr],
    seconds: u64,
    temp: &std::path::Path,
) -> Result<String, Failure> {
    let mut child = Command::new(&state.python)
        .arg("nn-classifier/predict.py")
        .args(args)
        .env("OMP_NUM_THREADS", "1")
        .env("MKL_NUM_THREADS", "1")
        .env("OPENBLAS_NUM_THREADS", "1")
        .env("TMPDIR", temp)
        .env("TORCHINDUCTOR_CACHE_DIR", temp.join("torch-cache"))
        .kill_on_drop(true)
        .stdout(std::process::Stdio::piped())
        .stderr(std::process::Stdio::piped())
        .spawn()
        .map_err(|e| {
            log::error!("Python launch: {e}");
            internal()
        })?;
    // Drain both pipes with hard diagnostic budgets. Timeout kills and reaps before releasing capacity.
    use tokio::io::AsyncReadExt;
    let mut stdout = child.stdout.take().unwrap().take(16384);
    let mut stderr = child.stderr.take().unwrap().take(16384);
    let read = async {
        let mut out = Vec::new();
        let mut err = Vec::new();
        let (a, b) = tokio::join!(stdout.read_to_end(&mut out), stderr.read_to_end(&mut err));
        a?;
        b?;
        let status = child.wait().await?;
        Ok::<_, std::io::Error>((status, out, err))
    };
    match timeout(Duration::from_secs(seconds), read).await {
        Err(_) => {
            let _ = child.kill().await;
            let _ = child.wait().await;
            log::error!("Python exceeded {seconds}s deadline");
            Err((StatusCode::GATEWAY_TIMEOUT, "Image processing timed out"))
        }
        Ok(Err(e)) => {
            log::error!("Python IO: {e}");
            Err(internal())
        }
        Ok(Ok((status, out, err))) => {
            if !status.success() {
                log::error!(
                    "Python {status}: {} {}",
                    String::from_utf8_lossy(&err),
                    String::from_utf8_lossy(&out)
                );
                return Err(if status.code() == Some(2) {
                    bad()
                } else {
                    internal()
                });
            }
            String::from_utf8(out).map_err(|_| internal())
        }
    }
}

// Only this directory is managed automatically; approved datasets are never touched.
fn prune(pending: &std::path::Path) -> std::io::Result<(usize, u64)> {
    fs::create_dir_all(pending)?;
    let mut count = 0;
    let mut bytes = 0;
    for label in ["match_ready", "not_match_ready"] {
        let directory = pending.join(label);
        fs::create_dir_all(&directory)?;
        for entry in fs::read_dir(directory)? {
            let entry = entry?;
            let meta = entry.metadata()?;
            if !meta.is_file() {
                continue;
            }
            if SystemTime::now()
                .duration_since(meta.modified()?)
                .unwrap_or_default()
                >= RETENTION
            {
                fs::remove_file(entry.path())?;
            } else {
                count += 1;
                bytes += meta.len();
            }
        }
    }
    Ok((count, bytes))
}

async fn process(
    state: Arc<State>,
    image: Vec<u8>,
    label: Option<String>,
) -> Result<Value, Failure> {
    let temp = TempDir::new().map_err(|_| internal())?;
    let input = temp.path().join("upload");
    let normalized = temp.path().join("image.jpg");
    fs::write(&input, image).map_err(|e| {
        log::error!("Temporary upload: {e}");
        internal()
    })?;
    let mode = if label.is_some() {
        "--normalize"
    } else {
        "--validate"
    };
    python(
        &state,
        &[mode.as_ref(), input.as_os_str(), normalized.as_os_str()],
        10,
        temp.path(),
    )
    .await?;
    if let Some(label) = label {
        let _lock = state.storage.acquire().await.map_err(|_| internal())?;
        let pending = state.pending.clone();
        return tokio::task::spawn_blocking(move || {
            // Hold the directory and serialization permit until the write has finished, even on disconnect.
            let _temp = temp;
            let (count, bytes) = prune(&pending).map_err(|e| { log::error!("Quarantine: {e}"); internal() })?;
            let size = fs::metadata(&normalized).map_err(|_| internal())?.len();
            if count >= MAX_PENDING_FILES || bytes + size > MAX_PENDING_BYTES { return Err(unavailable()); }
            let mut file = tempfile::Builder::new().prefix("contribution-").suffix(".jpg")
                .tempfile_in(pending.join(&label)).map_err(|_| internal())?;
            std::io::copy(&mut fs::File::open(normalized).map_err(|_| internal())?, &mut file).map_err(|_| internal())?;
            file.flush().map_err(|_| internal())?;
            let filename = file.path().file_name().unwrap().to_string_lossy().into_owned();
            file.keep().map_err(|_| internal())?;
            Ok(json!({"status": "success", "message": "Training data submitted successfully", "filename": filename, "label": label, "review_status": "pending"}))
        }).await.map_err(|_| internal())?;
    }
    let _permit = state
        .inference
        .clone()
        .try_acquire_owned()
        .map_err(|_| unavailable())?;
    let output = python(
        &state,
        &[input.as_os_str(), "--json".as_ref()],
        60,
        temp.path(),
    )
    .await?;
    let value: Value = serde_json::from_str(output.trim()).map_err(|_| internal())?;
    if !matches!(
        value["prediction"].as_str(),
        Some("match_ready" | "not_match_ready")
    ) || !value["confidence"]
        .as_f64()
        .is_some_and(|v| v.is_finite() && (0.0..=1.0).contains(&v))
    {
        return Err(internal());
    }
    Ok(value)
}

async fn upload(
    req: HttpRequest,
    payload: web::Payload,
    state: web::Data<Arc<State>>,
    training: bool,
) -> HttpResponse {
    let permit = match state.admission.clone().try_acquire_owned() {
        Ok(permit) => permit,
        Err(_) => return response(Err(unavailable())),
    };
    // Bound the entire multipart envelope too, including preambles and field headers.
    let stream = payload.scan(0usize, |total, chunk| {
        let result = chunk.and_then(|chunk| {
            *total = total.saturating_add(chunk.len());
            if *total > MAX_IMAGE + 64 * 1024 {
                Err(actix_web::error::PayloadError::Overflow)
            } else {
                Ok(chunk)
            }
        });
        futures_util::future::ready(Some(result))
    });
    let multipart = Multipart::new(req.headers(), stream);
    let parsed = timeout(Duration::from_secs(15), parse(multipart, training)).await;
    let (image, label) = match parsed {
        Ok(Ok(parsed)) => parsed,
        Ok(Err(e)) => return response(Err(e)),
        Err(_) => return HttpResponse::RequestTimeout().body("Upload timed out"),
    };
    let state = state.get_ref().clone();
    // Own capacity and temp files independently of the HTTP connection's lifetime.
    response(
        tokio::spawn(async move {
            let _permit = permit;
            process(state, image, label).await
        })
        .await
        .unwrap_or_else(|e| {
            log::error!("Processing task: {e}");
            Err(internal())
        }),
    )
}
async fn predict(
    req: HttpRequest,
    payload: web::Payload,
    state: web::Data<Arc<State>>,
) -> HttpResponse {
    upload(req, payload, state, false).await
}
async fn training(
    req: HttpRequest,
    payload: web::Payload,
    state: web::Data<Arc<State>>,
) -> HttpResponse {
    upload(req, payload, state, true).await
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init_from_env(env_logger::Env::default().default_filter_or("info"));
    let state = Arc::new(State {
        admission: Arc::new(Semaphore::new(2)),
        inference: Arc::new(Semaphore::new(1)),
        storage: Arc::new(Semaphore::new(1)),
        pending: std::env::var_os("TRAINING_PENDING_DIR")
            .map(PathBuf::from)
            .unwrap_or_else(|| "training_data/pending".into()),
        python: std::env::var("PYTHON_EXECUTABLE")
            .unwrap_or_else(|_| "nn-classifier/venv/bin/python3".into()),
    });
    prune(&state.pending)?;
    let cleanup = state.clone();
    tokio::spawn(async move {
        loop {
            tokio::time::sleep(Duration::from_secs(3600)).await;
            let _lock = cleanup.storage.acquire().await.unwrap();
            let path = cleanup.pending.clone();
            if let Err(e) = tokio::task::spawn_blocking(move || prune(&path))
                .await
                .unwrap()
            {
                log::error!("Retention cleanup: {e}");
            }
        }
    });
    let origins = std::env::var("ALLOWED_ORIGINS").unwrap_or_else(|_| {
        "https://alexheffernan.dev,https://alexanderheffernan.github.io".into()
    });
    // Retain the previous peer-IP burst/refill policy. Never trust arbitrary forwarded headers.
    let governor = actix_governor::GovernorConfigBuilder::default()
        .seconds_per_request(3)
        .burst_size(20)
        .finish()
        .unwrap();
    let limiter = governor.limiter();
    tokio::spawn(async move {
        loop {
            tokio::time::sleep(Duration::from_secs(60)).await;
            limiter.retain_recent();
            limiter.shrink_to_fit();
        }
    });
    let server = HttpServer::new(move || {
        let mut cors = Cors::default()
            .allowed_methods(vec!["POST"])
            .allowed_headers(vec![
                "Content-Type",
                "Authorization",
                "ngrok-skip-browser-warning",
            ]);
        for origin in origins.split(',') {
            cors = cors.allowed_origin(origin.trim());
        }
        App::new()
            .app_data(web::Data::new(state.clone()))
            .wrap(actix_web::middleware::Logger::new("%a %m %U %s %D"))
            .wrap(actix_governor::Governor::new(&governor))
            .wrap(cors)
            .route("/predict", web::post().to(predict))
            .route("/training", web::post().to(training))
    })
    .workers(2)
    .max_connections(128)
    .client_request_timeout(Duration::from_secs(15));
    // TLS remains the default; plain HTTP is opt-in for a loopback TLS-terminating proxy only.
    if std::env::var("HTTP_LOOPBACK").as_deref() == Ok("1") {
        server.bind(("127.0.0.1", 49161))?.run().await
    } else {
        use openssl::ssl::{SslAcceptor, SslFiletype, SslMethod};
        let mut tls = SslAcceptor::mozilla_intermediate(SslMethod::tls())?;
        tls.set_private_key_file("cricket-ready.key", SslFiletype::PEM)?;
        tls.set_certificate_chain_file("cricket-ready.crt")?;
        server.bind_openssl(("0.0.0.0", 49161), tls)?.run().await
    }
}
