"""
Match-Ready Cricket Ball Classifier - Prediction Script

Classifies cricket balls as match-ready or not match-ready using an ensemble of trained models.

Usage:
    python predict.py path/to/your/image.jpg # Replace with your image path

Examples:
    python predict.py test_images/ball1.jpg
    python predict.py /Users/username/Desktop/cricket_ball.jpg
"""

import json
import os
import sys
import warnings
from PIL import Image

MAX_BYTES = 5 * 1024 * 1024
MAX_PIXELS = 12_000_000
MAX_SIDE = 4096
Image.MAX_IMAGE_PIXELS = MAX_PIXELS
warnings.simplefilter("error", Image.DecompressionBombWarning)


def open_image(path):
    """Restrict decoders before sniffing, then bound dimensions before decoding pixels."""
    if os.path.getsize(path) > MAX_BYTES:
        raise ValueError("Image exceeds byte limit")
    with Image.open(path, formats=("JPEG", "PNG")) as image:
        width, height = image.size
        if not (0 < width <= MAX_SIDE and 0 < height <= MAX_SIDE and width * height <= MAX_PIXELS):
            raise ValueError("Image dimensions exceed limit")
        if getattr(image, "n_frames", 1) != 1:
            raise ValueError("Animated images are not accepted")
        image.load()
        return image.convert("RGB")


def normalize(source, destination):
    image = open_image(source)
    # A clean re-encode discards EXIF, comments, embedded profiles and trailing bytes.
    image.info.clear()
    image.save(destination, format="JPEG", quality=95)
    if os.path.getsize(destination) > MAX_BYTES:
        os.unlink(destination)
        raise ValueError("Normalized image exceeds byte limit")

def main():
    import torch
    import torch.nn as nn
    from torchvision import models, transforms
    import torch.nn.functional as F
    torch.set_num_threads(1)
    # Parameters
    models_dir = 'nn-classifier/models'   # Directory containing trained models
    model_paths = [os.path.join(models_dir, f"model_{i}.pth") for i in range(1,4)]
    class_names = ['match_ready', 'not_match_ready']
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cuda' if torch.cuda.is_available() else 'cpu')

    # Parse command line arguments
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        print(f"❌ Error: No image path provided.")
        sys.exit(1)


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

    # Image transform (same as test_transform)
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                            std=[0.229, 0.224, 0.225])
    ])

    # Load and preprocess image
    try:
        image = open_image(image_path)
        input_tensor = transform(image).unsqueeze(0).to(device)  # shape: [1, 3, 224, 224]
    except Exception as e:
        print(f"❌ Error loading image: {e}")
        sys.exit(1)

    # Load all models
    models_list = []
    for i, path in enumerate(model_paths):
        try:
            model = models.resnet18(weights=None)
            
            # Match the exact architecture from training script
            model.fc = nn.Sequential(
                nn.Dropout(0.5),  # Add dropout before final layer
                nn.Linear(model.fc.in_features, len(class_names))
            )
            
            model.load_state_dict(torch.load(path, map_location=device, weights_only=True))
            model.to(device)
            model.eval()  # Important: disable dropout during inference
            models_list.append(model)
        except Exception as e:
            print(f"❌ Error loading model {path}: {e}")
            sys.exit(1)

    # Predict with voting
    with torch.no_grad():
        # Collect all softmax probabilities
        probs = []
        for i, model in enumerate(models_list):
            outputs = model(input_tensor)
            prob = F.softmax(outputs, dim=1)
            probs.append(prob.cpu())
            individual_prediction = class_names[prob.argmax().item()]
            individual_confidence = prob.max().item()

        # Average probabilities
        avg_prob = torch.mean(torch.stack(probs), dim=0)
        predicted_class = torch.argmax(avg_prob, dim=1).item()
        confidence = avg_prob[0][predicted_class].item()
        label = class_names[predicted_class]

    # Display results
    if "--json" in sys.argv[2:]:
        print(json.dumps({"prediction": label, "confidence": round(confidence, 4)}))
    else:
        # Keep the desktop GUI and command-line output contract.
        print(f"Prediction: {label}; Confidence: {confidence:.4f}")

if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] in ("--normalize", "--validate"):
        try:
            if sys.argv[1] == "--normalize":
                normalize(sys.argv[2], sys.argv[3])
            else:
                open_image(sys.argv[2])
        except Exception as error:
            print(f"Image validation: {error}", file=sys.stderr)
            sys.exit(2)
    else:
        main()
