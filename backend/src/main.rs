mod request_logger;

use rusty_api;
use actix_multipart::Multipart;
use futures_util::StreamExt as _;
use bytes::BytesMut;
use chrono::Utc;
use std::process::Command;
use std::fs;
use std::path::Path;
use serde_json::{json, Value};

use request_logger::RequestLogger;

/// Parses the multipart payload, extracting the image data and optional label.
async fn parse_multipart(mut payload: Multipart) -> Result<(BytesMut, Option<String>), rusty_api::HttpResponse> {
    let mut image_bytes = BytesMut::new();
    let mut label = None;

    while let Some(item) = payload.next().await {
        let mut field = match item {
            Ok(f) => f,
            Err(e) => return Err(rusty_api::HttpResponse::BadRequest().body(format!("Multipart error: {e}"))),
        };

        match field.name() {
            "image" => {
                while let Some(chunk) = field.next().await {
                    let data = match chunk {
                        Ok(d) => d,
                        Err(e) => return Err(rusty_api::HttpResponse::InternalServerError().body(format!("Read error: {e}"))),
                    };
                    image_bytes.extend_from_slice(&data);
                }
            }
            "label" => {
                let mut label_data = BytesMut::new();
                while let Some(chunk) = field.next().await {
                    let data = match chunk {
                        Ok(d) => d,
                        Err(e) => return Err(rusty_api::HttpResponse::InternalServerError().body(format!("Read error: {e}"))),
                    };
                    label_data.extend_from_slice(&data);
                }
                label = Some(String::from_utf8_lossy(&label_data).to_string());
            }
            _ => {
                return Err(rusty_api::HttpResponse::BadRequest()
                    .body(format!("Unexpected field: {}", field.name())));
            }
        }
    }

    if image_bytes.is_empty() {
        return Err(rusty_api::HttpResponse::BadRequest().body("No image data received"));
    }

    Ok((image_bytes, label))
}

/// Parses the multipart payload for prediction (image only).
async fn parse_multipart_predict(mut payload: Multipart) -> Result<BytesMut, rusty_api::HttpResponse> {
    let mut image_bytes = BytesMut::new();

    while let Some(item) = payload.next().await {
        let mut field = match item {
            Ok(f) => f,
            Err(e) => return Err(rusty_api::HttpResponse::BadRequest().body(format!("Multipart error: {e}"))),
        };

        match field.name() {
            "image" => {
                while let Some(chunk) = field.next().await {
                    let data = match chunk {
                        Ok(d) => d,
                        Err(e) => return Err(rusty_api::HttpResponse::InternalServerError().body(format!("Read error: {e}"))),
                    };
                    image_bytes.extend_from_slice(&data);
                }
            }
            _ => {
                return Err(rusty_api::HttpResponse::BadRequest()
                    .body(format!("Unexpected field: {}", field.name())));
            }
        }
    }

    if image_bytes.is_empty() {
        return Err(rusty_api::HttpResponse::BadRequest().body("No image data received"));
    }

    Ok(image_bytes)
}

/// Training route handler for saving labeled cricket ball images.
/// Accepts multipart form-data with "image" and "label" fields.
async fn training_route(payload: Multipart) -> rusty_api::HttpResponse {
    let request_id = Utc::now().timestamp_millis();
    let logger = RequestLogger::new(request_id);

    logger.info("Received request to /training");

    // Parse multipart payload
    let (image_bytes, label) = match parse_multipart(payload).await {
        Ok((bytes, lbl)) => (bytes, lbl),
        Err(resp) => {
            logger.error("Failed to parse multipart payload");
            return resp;
        },
    };

    let label = match label {
        Some(l) => l,
        None => {
            logger.error("No label provided");
            return rusty_api::HttpResponse::BadRequest().body("Label is required for training data");
        }
    };

    // Validate label
    if label != "match_ready" && label != "not_match_ready" {
        logger.error(format!("Invalid label: {}", label));
        return rusty_api::HttpResponse::BadRequest()
            .body("Label must be either 'match_ready' or 'not_match_ready'");
    }

    logger.info(format!("Training image received: {} bytes, label: {}", image_bytes.len(), label));

    // Create training data directory structure
    let training_dir = "training_data";
    let label_dir = format!("{}/{}", training_dir, label);
    
    // Create directories if they don't exist
    if let Err(e) = fs::create_dir_all(&label_dir) {
        logger.error(format!("Failed to create training directory: {}", e));
        return rusty_api::HttpResponse::InternalServerError()
            .body(format!("Failed to create training directory: {}", e));
    }

    // Generate unique filename with timestamp
    let timestamp = Utc::now().format("%Y%m%d_%H%M%S_%3f");
    let filename = format!("cricket_ball_{}_{}.jpg", timestamp, request_id);
    let file_path = format!("{}/{}", label_dir, filename);

    // Write image to training directory
    if let Err(e) = fs::write(&file_path, &image_bytes) {
        logger.error(format!("Failed to write training image: {}", e));
        return rusty_api::HttpResponse::InternalServerError()
            .body(format!("Failed to write training image: {}", e));
    }

    logger.info(format!("Training image saved: {}", file_path));

    // Log training data submission for audit trail
    let log_entry = json!({
        "timestamp": Utc::now().to_rfc3339(),
        "request_id": request_id,
        "label": label,
        "filename": filename,
        "file_path": file_path,
        "image_size_bytes": image_bytes.len()
    });

    // Append to training log file
    let log_file = format!("{}/training_log.jsonl", training_dir);
    let log_line = format!("{}\n", log_entry.to_string());
    
    if let Err(e) = fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(&log_file)
        .and_then(|mut file| {
            use std::io::Write;
            file.write_all(log_line.as_bytes())
        })
    {
        logger.error(format!("Failed to write to training log: {}", e));
        // Don't fail the request if logging fails, just log the error
    }

    // Return success response
    let response = json!({
        "status": "success",
        "message": "Training data saved successfully",
        "filename": filename,
        "label": label,
        "request_id": request_id
    });

    match serde_json::to_string(&response) {
        Ok(json) => {
            logger.info(format!("Training data saved successfully: {}", filename));
            rusty_api::HttpResponse::Ok()
                .content_type("application/json")
                .body(json)
        }
        Err(e) => {
            logger.error(format!("Serialization error: {}", e));
            rusty_api::HttpResponse::InternalServerError()
                .body(format!("Serialization error: {}", e))
        }
    }
}

/// Main route handler for cricket ball prediction.
/// Accepts multipart form-data with "image" field.
async fn predict_image_route(payload: Multipart) -> rusty_api::HttpResponse {
    let request_id = Utc::now().timestamp_millis();
    let logger = RequestLogger::new(request_id);

    logger.info("Received request to /predict");

    // Parse multipart payload
    let image_bytes = match parse_multipart_predict(payload).await {
        Ok(bytes) => bytes,
        Err(resp) => {
            logger.error("Failed to parse multipart payload");
            return resp;
        },
    };

    logger.info(format!("Image received: {} bytes", image_bytes.len()));

    // Create temporary file for the image
    let temp_path = format!("/tmp/cricket_ball_{}.jpg", request_id);
    
    // Write image to temporary file
    if let Err(e) = fs::write(&temp_path, &image_bytes) {
        logger.error(format!("Failed to write temporary file: {}", e));
        return rusty_api::HttpResponse::InternalServerError()
            .body(format!("Failed to write temporary file: {}", e));
    }

    logger.info(format!("Temporary file created: {}", temp_path));

    // Call the Python prediction script
    let output = match Command::new("nn-classifier/venv/bin/python3")
        .arg("nn-classifier/predict.py")
        .arg(&temp_path)
        .current_dir(".")  // Run from backend directory
        .output()
    {
        Ok(output) => output,
        Err(e) => {
            logger.error(format!("Failed to execute predict.py: {}", e));
            // Clean up temp file
            fs::remove_file(&temp_path).ok();
            return rusty_api::HttpResponse::InternalServerError()
                .body(format!("Failed to execute prediction: {}", e));
        }
    };

    // Clean up temporary file
    if let Err(e) = fs::remove_file(&temp_path) {
        logger.error(format!("Failed to clean up temp file: {}", e));
    }

    // Check if the command executed successfully
    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        logger.error(format!("Prediction script failed: {}", stderr));
        return rusty_api::HttpResponse::InternalServerError()
            .body(format!("Prediction failed: {}", stderr));
    }

    // Parse the prediction output
    let stdout = String::from_utf8_lossy(&output.stdout);
    logger.info("Prediction completed successfully");

    // Extract prediction results from the output
    // The predict.py script outputs structured text, so we'll parse it
    let prediction_result = parse_prediction_output(&stdout);
    
    match serde_json::to_string(&prediction_result) {
        Ok(json) => {
            logger.info(format!("Returning prediction: {}", json));
            rusty_api::HttpResponse::Ok()
                .content_type("application/json")
                .body(json)
        }
        Err(e) => {
            logger.error(format!("Serialization error: {}", e));
            rusty_api::HttpResponse::InternalServerError()
                .body(format!("Serialization error: {}", e))
        }
    }
}

/// Parse the output from predict.py script into a structured JSON response
fn parse_prediction_output(output: &str) -> Value {
    let lines: Vec<&str> = output.lines().collect();
    let mut prediction = "unknown";
    let mut confidence = 0.0;

    // Parse the prediction output - new format: "Prediction: {label}; Confidence: {confidence:.4f}"
    for line in lines {
        if line.contains("Prediction:") && line.contains("Confidence:") {
            // Extract prediction label
            if let Some(pred_start) = line.find("Prediction: ") {
                let after_pred = &line[pred_start + 12..];
                if let Some(pred_end) = after_pred.find(';') {
                    let pred_str = after_pred[..pred_end].trim();
                    if pred_str == "match_ready" || pred_str == "not_match_ready" {
                        prediction = pred_str;
                    }
                }
            }
            
            // Extract confidence value
            if let Some(conf_start) = line.find("Confidence: ") {
                let conf_str = &line[conf_start + 12..];
                if let Ok(conf) = conf_str.trim().parse::<f64>() {
                    confidence = conf;
                }
            }
        }
    }

    json!({
        "prediction": prediction,
        "confidence": confidence
    })
}

/// Entrypoint: sets up API routes, TLS, CORS, and starts the server.
fn main() {
    let routes = rusty_api::Routes::new()
        .add_route(rusty_api::Method::POST, "/predict", predict_image_route)
        .add_route(rusty_api::Method::POST, "/training", training_route);

    rusty_api::Api::new()
        .certs("cricket-ready.crt", "cricket-ready.key")
        .rate_limit(3, 20)
        .bind("0.0.0.0", 49161)
        .configure_routes(routes)
        .configure_cors(|| {
            rusty_api::Cors::default()
                .allow_any_origin()
                .allow_any_method()
                .allowed_header("ngrok-skip-browser-warning")
        })
        .start();
}