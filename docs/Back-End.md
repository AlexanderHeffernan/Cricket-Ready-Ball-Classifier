# Overview

The back-end powers the Cricket-Ready Ball Classifier web application, providing a secure API for image prediction and training data collection. It is built in Rust for performance and reliability, and leverages a Python neural network for image classification. The back-end is designed to run on a Raspberry Pi or similar Linux device.

---

## Technology Stack

- **Rust**: Main API server using Actix directly (configuration owned by this repository)
- **Python**: Neural network classifier (PyTorch, torchvision)

---

## Installation & Deployment

1. **Run the install script:**
   ```bash
    curl -sSL https://raw.githubusercontent.com/AlexanderHeffernan/Cricket-Ready-Ball-Classifier/main/backend/install-cricket-ready-backend.sh -o install-cricket-ready-backend.sh
    chmod +x install-cricket-ready-backend.sh
    ./install-cricket-ready-backend.sh
    ```
    - Builds the Rust sources with Cargo; downloads Python scripts and models
    - Requires a current Rust toolchain, OpenSSL development headers and Python >=3.11
    - Setups up Python virtual environment and installs dependencies
    - Generates TLS certificates if needed
    - Configures and starts a systemd service

2. **Access the API:**
    - Default port: `49161`
    - Endpoints: `/predict`, `/training`
    - TLS enabled by default

3. **Logs:**
    - API requests and diagnostics: service stderr/journal

See [Security and operations](Back-End.Security.md) before deploying. Public
contributions now require review in an expiring quarantine. A non-root,
resource-limited container recipe with persistent storage is provided in
`backend/compose.yaml`; adopting it and migrating existing data require separate
deployment approval.

---

## Neural Network Classifier

- **Location:** `backend/nn-classifier/`
- **Model:** Ensemble of three ResNet18 models (`models/model_1.pth`, etc.)
- **Training:**
  - Run `train.py` to retrain models using images in `dataset/`
  - Data augmentation and cross-validation are used
- **Prediction:**
  - Run `predict.py` to classify images

---

## References

- [Rust API Source](../backend/src/main.rs)
- [Python Classifier](../backend/nn-classifier/predict.py)
- [Training Script](../backend/nn-classifier/train.py)
- [Install Script](../backend/install-cricket-ready-backend.sh)
