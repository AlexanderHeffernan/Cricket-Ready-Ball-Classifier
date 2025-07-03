"""
Match-Ready Cricket Ball Classifier - Prediction Script

Classifies cricket balls as match-ready or not match-ready using an ensemble of trained models.

Usage:
    python predict.py path/to/your/image.jpg # Replace with your image path

Examples:
    python predict.py test_images/ball1.jpg
    python predict.py /Users/username/Desktop/cricket_ball.jpg
"""

# Check for required dependencies
try:
    import torch
    import torch.nn as nn
    from torchvision import models, transforms
    from PIL import Image
    import os
    import sys
    import torch.nn.functional as F
except ImportError as e:
    print(f"❌ Missing required package: {e}")
    print("💡 Install required packages with:")
    print("   pip install torch torchvision pillow")
    print("   Or use: pip install -r requirements.txt")
    exit(1)

def main():
    # Parameters
    models_dir = 'models'   # Directory containing trained models
    model_paths = [os.path.join(models_dir, f"model_{i}.pth") for i in range(1,4)]
    class_names = ['match_ready', 'not_match_ready']
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cuda' if torch.cuda.is_available() else 'cpu')

    print(f"✅ All dependencies loaded successfully!")

    # Parse command line arguments
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        print(f"🖼️  Using image from command line: {image_path}")
    else:
        print(f"❌ Error: No image path provided.")
        return


    # Validate image path
    if not os.path.exists(image_path):
        print(f"❌ Error: Image file '{image_path}' does not exist.")
        print(f"💡 Usage: python {sys.argv[0]} <path_to_image>")
        print(f"💡 Example: python {sys.argv[0]} test_images/my_ball.jpg")
        sys.exit(1)

    # Check if models directory exists
    if not os.path.exists(models_dir):
        print(f"❌ Error: Models directory '{models_dir}' does not exist.")
        print("💡 Please train the model first by running: python train.py")
        sys.exit(1)

    # Check if all model files exist
    missing_models = [path for path in model_paths if not os.path.exists(path)]
    if missing_models:
        print(f"❌ Error: Missing model files:")
        for path in missing_models:
            print(f"   - {path}")
        print("💡 Please train the model first by running: python train.py")
        sys.exit(1)

    print(f"📁 Loading models from: {models_dir}")
    print(f"🖥️  Using device: {device}")

    # Image transform (same as test_transform)
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                            std=[0.229, 0.224, 0.225])
    ])

    # Load and preprocess image
    try:
        image = Image.open(image_path).convert('RGB')
        input_tensor = transform(image).unsqueeze(0).to(device)  # shape: [1, 3, 224, 224]
        print(f"✅ Image loaded and preprocessed: {os.path.basename(image_path)}")
        print(f"   📏 Original size: {image.size}")
        print(f"   📏 Processed size: 224x224")
    except Exception as e:
        print(f"❌ Error loading image: {e}")
        sys.exit(1)

    # Load all models
    print(f"\n🧠 Loading {len(model_paths)} trained models...")
    models_list = []
    for i, path in enumerate(model_paths):
        try:
            print(f"   Loading model {i+1}: {os.path.basename(path)}")
            model = models.resnet18(weights=None)
            
            # Match the exact architecture from training script
            model.fc = nn.Sequential(
                nn.Dropout(0.5),  # Add dropout before final layer
                nn.Linear(model.fc.in_features, len(class_names))
            )
            
            model.load_state_dict(torch.load(path, map_location=device))
            model.to(device)
            model.eval()  # Important: disable dropout during inference
            models_list.append(model)
        except Exception as e:
            print(f"❌ Error loading model {path}: {e}")
            sys.exit(1)

    print(f"✅ All models loaded successfully!")

    # Predict with voting
    print(f"\n🔮 Running inference...")
    with torch.no_grad():
        # Collect all softmax probabilities
        probs = []
        for i, model in enumerate(models_list):
            outputs = model(input_tensor)
            prob = F.softmax(outputs, dim=1)
            probs.append(prob.cpu())
            individual_prediction = class_names[prob.argmax().item()]
            individual_confidence = prob.max().item()
            print(f"   Model {i+1}: {individual_prediction} ({individual_confidence:.4f})")

        # Average probabilities
        avg_prob = torch.mean(torch.stack(probs), dim=0)
        predicted_class = torch.argmax(avg_prob, dim=1).item()
        confidence = avg_prob[0][predicted_class].item()
        label = class_names[predicted_class]

    # Display results
    print("\n" + "="*60)
    print("📊 ENSEMBLE PREDICTION RESULTS")
    print("="*60)
    print(f"🖼️  Image: {os.path.basename(image_path)}")
    print(f"✅ Final Prediction: {label.upper()}")
    print(f"📊 Confidence: {confidence:.4f} ({confidence*100:.2f}%)")
    print(f"📊 Individual Probabilities:")
    print(f"   🟢 {class_names[0]}: {avg_prob[0][0]:.4f} ({avg_prob[0][0]*100:.2f}%)")
    print(f"   🔴 {class_names[1]}: {avg_prob[0][1]:.4f} ({avg_prob[0][1]*100:.2f}%)")
    print("="*60)

    # Interpretation
    if confidence > 0.9:
        print("💪 Very confident prediction!")
    elif confidence > 0.7:
        print("👍 Confident prediction")
    else:
        print("⚠️  Low confidence - consider manual inspection")

if __name__ == "__main__":
    main()