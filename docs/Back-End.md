# Overview

The back-end powers the Cricket-Ready Ball Classifier web application, providing a secure API for image prediction and training data collection. It is built in Rust for performance and reliability, and leverages a Python neural network for image classification. The back-end is designed to run on a Raspberry Pi or similar Linux device.

---

## Technology Stack

- **Rust**: Main API server (using [`rusty-api`](https://github.com/AlexanderHeffernan/rusty-api))
- **Python**: Neural network classifier (PyTorch, torchvision)

---

## Installation & Deployment

1. **Run the install script:**
   ```bash
    curl -sSL https://raw.githubusercontent.com/AlexanderHeffernan/Cricket-Ready-Ball-Classifier/main/backend/install-cricket-ready-backend.sh -o install-cricket-ready-backend.sh
    chmod +x install-cricket-ready-backend.sh
    ./install-cricket-ready-backend.sh
    ```
    - Downloads the back-end binary, Python scripts, and models
    - Setups up Python virtual environment and installs dependencies
    - Generates TLS certificates if needed
    - Configures and starts a systemd service

2. **Access the API:**
    - Default port: `49160`
    - Endpoints: `/predict`, `/train`
    - TLS enabled by default

3. **Logs:**
    - API requests: `backend.log`

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