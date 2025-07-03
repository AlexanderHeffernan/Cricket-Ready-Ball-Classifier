import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import os
import torch.nn.functional as F

# Parameters
models_dir = 'models'   # Directory containing trained models
model_paths = [os.path.join(models_dir, f"model_{i}.pth") for i in range(1,4)]
image_path = "test_images/test.jpg"  # Update path to use folder
class_names = ['match_ready', 'not_match_ready']
device = torch.device('mps' if torch.backends.mps.is_available() else 'cuda' if torch.cuda.is_available() else 'cpu')

# Check if models directory exists
if not os.path.exists(models_dir):
    raise FileNotFoundError(f"Models directory '{models_dir}' does not exist. Please train the model first.")

# Check if all model files exist
for path in model_paths:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model file '{path}' does not exist. Please train the model first.")

print(f"📁 Loading models from: {models_dir}")

# Image transform (same as test_transform)
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# Load image
if not os.path.exists(image_path):
    raise FileNotFoundError(f"Image file '{image_path}' does not exist.")

image = Image.open(image_path).convert('RGB')
input_tensor = transform(image).unsqueeze(0).to(device)  # shape: [1, 3, 224, 224]

# Load all models
print(f"🧠 Loading {len(model_paths)} trained models...")
models_list = []
for i, path in enumerate(model_paths):
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

print(f"✅ All models loaded successfully!")

# Predict with voting
with torch.no_grad():
    # Collect all softmax probabilities
    probs = []
    for i, model in enumerate(models_list):
        outputs = model(input_tensor)
        prob = F.softmax(outputs, dim=1)
        probs.append(prob.cpu())
        print(f"   Model {i+1} prediction: {class_names[prob.argmax().item()]} ({prob.max().item():.4f})")

    # Average probabilities
    avg_prob = torch.mean(torch.stack(probs), dim=0)
    predicted_class = torch.argmax(avg_prob, dim=1).item()
    confidence = avg_prob[0][predicted_class].item()
    label = class_names[predicted_class]

print("\n" + "="*50)
print("📊 ENSEMBLE PREDICTION RESULTS")
print("="*50)
print(f"✅ Final Prediction: {label}")
print(f"📊 Confidence: {confidence:.4f} ({confidence*100:.2f}%)")
print(f"📊 Probabilities:")
print(f"   {class_names[0]}: {avg_prob[0][0]:.4f} ({avg_prob[0][0]*100:.2f}%)")
print(f"   {class_names[1]}: {avg_prob[0][1]:.4f} ({avg_prob[0][1]*100:.2f}%)")
print("="*50)