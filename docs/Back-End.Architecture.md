# Architecture

## Folder Structure

- `src/` – Rust backend source code
- `nn-classifier/` – Python neural network scripts and data (see separate docs)
- `training_data/` – Collected training images and logs
- `models/` – Trained model files
- `bin/` – Compiled Rust binaries

## Design

- **Rust API**: Handles HTTP requests, CORS, rate limiting, and logging.
- **Python Integration**: Rust backend calls Python scripts for prediction/training.

## Key Files

- `main.rs` – Main entry point for the Rust backend.
- `request_logger.rs` – Middleware for logging requests.
- `Cargo.toml` – Rust dependencies and build config.