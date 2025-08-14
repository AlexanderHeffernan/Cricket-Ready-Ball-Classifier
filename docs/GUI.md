# Overview

The GUI is a desktop application for managing datasets, training models, and testing predictions for the Cricket-Ready Ball Classifier project. It is built with Python and PyQt5, and is designed for local use on Windows, macOS, or Linux.

## Features

- **Dataset Management**: Upload and manage images for training and testing.
- **Model Training**: Configure and start training neural network models.
- **Prediction**: Select images for prediction and view results.
- **Model Management**: View and manage trained models.

## Technology Stack

- **Framework**: PyQt5
- **Styling**: CSS3
- **Deployment**: Python virtual environment

## Development Setup

```bash
# Create a virtual environment
python3 -m venv venv --system-site-packages
# Activate the virtual environment
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
# Install PyQt5
pip install PyQt5
# Run the GUI application
python3 main.py
```