# Match-Ready Cricket Ball Classifier 🏏

A deep learning model to classify cricket balls as **match-ready** or **not match-ready** using PyTorch and ResNet18.

## Features ✨

- **98.96% average accuracy** with 3-fold cross-validation
- **Ensemble voting** from 3 trained models for robust predictions
- **Pre-trained models included** - no training required to get started
- **Data augmentation and early stopping** for optimal performance
- **Easy-to-use prediction script** with command-line interface
- **Reproducible results** with fixed random seeds

## Quick Start 🚀

### Option A: Use Pre-trained Models (Recommended)

**No training required!** Pre-trained models with 98.9% accuracy are included.

```bash
# 1. Install dependencies
pip install torch torchvision pillow scikit-learn numpy

# 2. Run prediction on your image
python predict.py path/to/your/cricket_ball.jpg

# Example with test images
python predict.py test_images/my_ball.jpg
```

### Option B: Train Your Own Models

Want to train on your own dataset? Follow these steps:

```bash
# 1. Install dependencies
pip install torch torchvision pillow scikit-learn numpy

# 2. Prepare your dataset
# Add images to:
#   dataset/match_ready/     - Put match-ready ball images here
#   dataset/not_match_ready/ - Put non-match-ready ball images here

# 3. Train models (this will replace the pre-trained ones)
python train.py

# 4. Test your new models
python predict.py path/to/your/image.jpg
```

## Usage Examples 📖

```bash
# Use default test image
python predict.py

# Predict on a specific image
python predict.py test_images/cricket_ball_1.jpg

# Predict on any image file
python predict.py /Users/alex/Desktop/my_cricket_ball.png
```

**Sample Output:**
```
============================================================
📊 ENSEMBLE PREDICTION RESULTS
============================================================
🖼️  Image: cricket_ball_1.jpg
✅ Final Prediction: MATCH_READY
📊 Confidence: 0.9234 (92.34%)
📊 Individual Probabilities:
   🟢 match_ready: 0.9234 (92.34%)
   🔴 not_match_ready: 0.0766 (7.66%)
============================================================
💪 Very confident prediction!
```

## Project Structure 📁

```
cricket_ball_classifier/
├── dataset/              # Training dataset (empty - add your images here)
│   ├── match_ready/      # Match-ready cricket ball images
│   └── not_match_ready/  # Non-match-ready cricket ball images
├── models/               # Pre-trained models (included)
│   ├── model_1.pth       # First ensemble model
│   ├── model_2.pth       # Second ensemble model
│   └── model_3.pth       # Third ensemble model
├── test_images/          # Test images for prediction (add your test images)
├── train.py              # Training script
├── predict.py            # Prediction script
├── requirements.txt      # Python dependencies
├── .gitignore           # Git ignore file
└── README.md            # This file
```

## Model Performance 📊

**Cross-Validation Results:**
- **Average Accuracy:** 98.96%
- **Standard Deviation:** 0.0147
- **Best Fold:** 100.00%
- **Worst Fold:** 96.88%

**Technical Details:**
- **Architecture:** ResNet18 with transfer learning
- **Training Data:** 96 curated cricket ball images
- **Validation:** 3-fold cross-validation
- **Ensemble:** 3 models with voting
- **Data Augmentation:** Rotation, flipping, resizing
- **Early Stopping:** Prevents overfitting

## Pre-trained Models 🎯

This repository includes pre-trained models that achieve **97.9% accuracy**. These models were trained on a carefully curated dataset of cricket ball images and can be used immediately without any training.

**Model Details:**
- Trained on 96 high-quality cricket ball images
- Uses ResNet18 architecture with transfer learning
- Ensemble of 3 models for robust predictions
- Models are optimized for both accuracy and confidence

## Requirements 📋

- **Python 3.7+**
- **PyTorch** (>=1.9.0)
- **torchvision** (>=0.10.0)
- **Pillow** (>=8.0.0)
- **scikit-learn** (>=1.0.0)
- **numpy** (>=1.21.0)

Install all requirements:
```bash
pip install -r requirements.txt
```

## Training Details 🔧

If you want to train your own models:

1. **Dataset Structure:** Organize images in `dataset/match_ready/` and `dataset/not_match_ready/`
2. **Minimum Images:** At least 20-30 images per class recommended
3. **Image Format:** JPG, PNG, or other common formats
4. **Training Time:** ~1-4 minutes on modern hardware
5. **GPU Support:** Automatically uses MPS (Apple Silicon) or CUDA if available

**Training Features:**
- Transfer learning from ImageNet
- Data augmentation for robustness
- Early stopping to prevent overfitting
- Learning rate scheduling
- Cross-validation for reliable results

## Contributing 🤝

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Acknowledgments 🙏

- Built with PyTorch and torchvision
- ResNet architecture from "Deep Residual Learning for Image Recognition"
- Inspired by the need for automated cricket equipment assessment

---

**Happy Cricket Ball Classification! 🏏**

For questions or issues, please open a GitHub issue.