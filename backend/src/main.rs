mod request_logger;

use rusty_api;
use actix_multipart::Multipart;
use futures_util::StreamExt as _;
use bytes::BytesMut;
use chrono::Utc;
use std::process::Command;
use std::fs;
use serde_json::{json, Value};

use request_logger::RequestLogger;

/// Parses the multipart payload, extracting the image data.
async fn parse_multipart(mut payload: Multipart) -> Result<BytesMut, rusty_api::HttpResponse> {
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

/// Main route handler for cricket ball prediction.
/// Accepts multipart form-data with "image" field.
async fn predict_image_route(payload: Multipart) -> rusty_api::HttpResponse {
    let request_id = Utc::now().timestamp_millis();
    let logger = RequestLogger::new(request_id);

    logger.info("Received request to /predict");

    // Parse multipart payload
    let image_bytes = match parse_multipart(payload).await {
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
    let mut match_ready_prob = 0.0;
    let mut not_match_ready_prob = 0.0;
    let mut image_name = "uploaded_image";

    // Parse the prediction output
    for line in lines {
        if line.contains("Final Prediction:") {
            if line.contains("MATCH_READY") {
                prediction = "match_ready";
            } else if line.contains("NOT_MATCH_READY") {
                prediction = "not_match_ready";
            }
        } else if line.contains("Confidence:") {
            // Extract confidence percentage
            if let Some(start) = line.find("Confidence: ") {
                let confidence_str = &line[start + 12..];
                if let Some(end) = confidence_str.find(' ') {
                    if let Ok(conf) = confidence_str[..end].parse::<f64>() {
                        confidence = conf;
                    }
                }
            }
        } else if line.contains("match_ready:") {
            // Extract match_ready probability
            if let Some(start) = line.find("match_ready: ") {
                let prob_str = &line[start + 13..];
                if let Some(end) = prob_str.find(' ') {
                    if let Ok(prob) = prob_str[..end].parse::<f64>() {
                        match_ready_prob = prob;
                    }
                }
            }
        } else if line.contains("not_match_ready:") {
            // Extract not_match_ready probability
            if let Some(start) = line.find("not_match_ready: ") {
                let prob_str = &line[start + 17..];
                if let Some(end) = prob_str.find(' ') {
                    if let Ok(prob) = prob_str[..end].parse::<f64>() {
                        not_match_ready_prob = prob;
                    }
                }
            }
        } else if line.contains("Image:") {
            // Extract image name
            if let Some(start) = line.find("Image: ") {
                let name_start = start + 7;
                if let Some(end) = line[name_start..].find('\n') {
                    image_name = &line[name_start..name_start + end];
                } else {
                    image_name = &line[name_start..];
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
        .add_route(rusty_api::Method::POST, "/predict", predict_image_route);

    rusty_api::Api::new()
        .certs("certs/cert.pem", "certs/key.pem")
        .rate_limit(3, 20)
        .bind("0.0.0.0", 8445)
        .configure_routes(routes)
        .configure_cors(|| {
            rusty_api::Cors::default()
                .allow_any_origin()
                .allow_any_method()
                .allowed_header("ngrok-skip-browser-warning")
        })
        .start();
}