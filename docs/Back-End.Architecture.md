# Architecture

## Folder Structure

- `src/` – Rust backend source code
- `nn-classifier/` – Python neural network scripts and data (see separate docs)
- `training_data/pending/` – Expiring, quota-limited contributions awaiting human review
- `models/` – Trained model files
- `Dockerfile`, `compose.yaml` – Opt-in isolated deployment and persistent contribution volume

## Design

- **Rust API**: Handles HTTP requests, CORS, rate limiting, and logging.
- **Python Integration**: Async, timed subprocesses validate images and run one inference at a time.

## Key Files

- `main.rs` – Main entry point for the Rust backend.
- Request metadata and bounded internal diagnostics go to service stderr.
- `Cargo.toml` – Rust dependencies and build config.
