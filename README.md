# Cricket-Ready Ball Classifier 🏏

Cricket-Ready Ball Classifier is a full-stack application that helps users determine if a cricket ball is match-ready using image classification powered by neural networks. The project features a modern, mobile-friendly front-end for capturing and uploading images, a robust back-end for processing predictions and collecting new training data, and a desktop GUI for advanced dataset management and model training.

---

## Features

- **Instant predictions**: Upload or capture a photo to get a match-readiness verdict in seconds.
- **Mobile-first front-end**: Responsive Vue.js web app for seamless use on any device.
- **Training tool**: Users can contribute new labeled images to improve the model.
- **Desktop GUI**: Manage datasets, train models, and test predictions locally.
- **Robust back-end**: Rust API server orchestrates image handling and model inference via Python. Built with [`rusty-api`](https://github.com/AlexanderHeffernan/rusty-api).
- **Neural network ensemble**: High-accuracy PyTorch models for reliable results.
- **Easy back-end deployment**: Designed for platforms like Raspberry Pi 5 and cloud hosting.
- **Open dataset growth**: Community-driven data collection for ongoing model improvement.

---

## Documentation

Full documentation is available in the [`docs/`](docs/) folder and is auto-synced to the [GitHub Wiki](https://github.com/AlexanderHeffernan/Cricket-Ready-Ball-Classifier/wiki).

### Key Docs:

- [Front-End Overview](docs/Front-End.md)
- [Back-End Overview](docs/Back-End.md)
- [GUI Overview](docs/GUI.md)
- [Neural Network Classifier Overview](docs/NN-Classifier.md)

---

## Architecture Overview

- **Front-End**:
  - Built with Vue.js + TypeScript
  - Camera/photo upload, prediction display, and training tool
  - Deployed via [GitHub Pages](https://alexanderheffernan.github.io/Cricket-Ready-Ball-Classifier/)

- **Back-End**:
  - Rust API server (built with [`rusty-api`](https://github.com/AlexanderHeffernan/rusty-api))
  - Handles image uploads, prediction requests, and training data submissions
  - Invokes Python scripts for neural network inference (PyTorch)
  - Exposed securely via Cloudflare Tunnel

- **Neural Networks**:
  - PyTorch-based CNN ensemble
  - Pre-trained models included
  - Supports retraining with new labeled data

- **Desktop GUI**:
  - PyQt5-based application for dataset management, model training, and prediction testing
  - Modular, cross-platform design

For a detailed breakdown, see the [docs folder](docs/) or the [GitHub Wiki](https://github.com/AlexanderHeffernan/Cricket-Ready-Ball-Classifier/wiki).

---

## Quick Start

### 1. Front-End

```bash
cd frontend
npm install
npm run serve
```

### 2. Back-End

You have two options for running the back-end:

**Option 1: Local Development**

```bash
cd backend
cargo run
```

**Option 2: Production Deployment**

Use the provided install and uninstall scripts to set up the back-end as a background service:

Install:

```bash
curl -sSL https://raw.githubusercontent.com/AlexanderHeffernan/Cricket-Ready-Ball-Classifier/main/backend/install-cricket-ready-backend.sh -o install-cricket-ready-backend.sh
chmod +x install-cricket-ready-backend.sh
./install-cricket-ready-backend.sh
```

Uninstall:

```bash
curl -sSL https://raw.githubusercontent.com/AlexanderHeffernan/Cricket-Ready-Ball-Classifier/main/backend/uninstall-cricket-ready-backend.sh | bash
```

### 3. Desktop GUI

```bash
cd gui
# On Raspberry Pi:
sudo apt install python3-pyqt5
python3 -m venv venv --system-site-packages
source venv/bin/activate
# On other platforms:
pip install PyQt5
python main.py
```

### 4. Configuration

- Set the backend API URL in the front-end via `.env` file:
  ```env
  VUE_APP_BACKEND_URL=https://api.alexheffernan.dev
  ```

---

## Usage

- **Prediction**:  
   Open the web app, capture or upload a cricket ball image, and view the match-readiness result and confidence score.

- **Training Tool**:  
   Switch to the training mode to capture and label new images, helping expand the dataset for future model improvements.

- **Desktop GUI**:  
   Use the GUI for advanced dataset management, model training, and local prediction testing.

---

## Project Structure

```
Cricket-Ready-Ball-Classifier/
├── backend/      # Rust API server, Python model scripts, install scripts
├── frontend/     # Vue.js web app (src, public, styles)
├── gui/          # PyQt5 desktop GUI
├── docs/         # Project documentation (auto-synced to GitHub Wiki)
└── README.md     # This file
```

---

## Requirements

- **Front-End**: Node.js, npm
- **Back-End**: Rust, Python, PyTorch, torchvision, pillow, scikit-learn, numpy
- **GUI**: Python 3.8+, PyQt5

---

## Contributing

Contributions are welcome! Please see the [docs](docs/) or [GitHub Wiki](https://github.com/AlexanderHeffernan/Cricket-Ready-Ball-Classifier/wiki) for guidelines, architecture, and development notes.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your fork and open a Pull Request

---