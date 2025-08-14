# Architecture

## Folder Structure

- `predict.py` – Script for running predictions on images.
- `train.py` – Script for training the ensemble of models.
- `requirements.txt` – Python dependencies.
- `dataset/` – Training images, organized by class.
- `models/` – Saved PyTorch model files.
- `test_images/` – Images for manual or automated testing.

## Model Design

- **Ensemble of 3 ResNet18 models** (PyTorch)
- Each model is trained with cross-validation and data augmentation
- Final prediction is based on majority vote or averaged confidence

## Integration

- Called by the Rust backend via subprocess for prediction and training