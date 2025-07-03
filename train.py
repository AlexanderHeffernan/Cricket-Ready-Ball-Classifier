"""
Cricket Ball Classifier - Training Script

Trains an ensemble of models to classify cricket balls as match-ready or not match-ready.

Usage:
    python train.py
"""

import os
import torch
import torch.nn as nn
import numpy as np
import random
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import datasets, models, transforms
from sklearn.model_selection import KFold

# ----------------------
# Configuration Parameters
# ----------------------
dataset_dir = 'dataset' # Directory containing the dataset of cricket ball images
models_dir = 'models'   # Directory to save trained models

# Create models directory if it doesn't exist
if not os.path.exists(models_dir):
    os.makedirs(models_dir)
    print(f"📁 Created models directory: {models_dir}")

if not os.path.exists(dataset_dir):
    raise FileNotFoundError(f"Dataset directory '{dataset_dir}' does not exist. Please check the path.")

batch_size = 16         # Number of images processed together
num_epochs = 15         # How many times to go through the training data
learning_rate = 0.001   # How fast the model learns (step size)
num_classes = 2         # Match-ready vs non-match-ready (2 classes)
k_folds = 3             # Split data into 5 parts for cross-validation

# Use Apple Silicon GPU if available, otherwise CUDA GPU, otherwise CPU
device = torch.device('mps' if torch.backends.mps.is_available() else 'cuda' if torch.cuda.is_available() else 'cpu')

# ----------------------
# Set Random Seeds for Reproducibility
# ----------------------
def set_seed(seed=42):
    """Set all random seeds for reproducible results"""
    random.seed(seed)                    # Python random module
    np.random.seed(seed)                # NumPy random
    torch.manual_seed(seed)             # PyTorch CPU random
    torch.cuda.manual_seed(seed)        # PyTorch GPU random
    torch.cuda.manual_seed_all(seed)    # All GPU devices
    torch.backends.cudnn.deterministic = True  # Deterministic convolutions
    torch.backends.cudnn.benchmark = False     # Disable optimization for reproducibility
    os.environ['PYTHONHASHSEED'] = str(seed)   # Python hash seed

# Call this before any other operations
set_seed(42)
print(f"🎲 Random seed set to 42 for reproducible results")

# ----------------------
# Image Preprocessing Transforms
# ----------------------
# Training transforms: Add variations to prevent overfitting
train_transform = transforms.Compose([
    transforms.Resize((256, 256)),                    # Resize larger first
    transforms.RandomResizedCrop(224, scale=(0.8, 1.0)), # Random crop with scale
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(20),                    # Increased rotation
    transforms.RandomVerticalFlip(p=0.1),            # Small chance of vertical flip
    transforms.ColorJitter(brightness=0.1, contrast=0.1), # Minimal color changes
    transforms.RandomAffine(degrees=0, translate=(0.05, 0.05)), # Small translation
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Test transforms: No randomization, just basic preprocessing
test_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# ----------------------
# Custom Dataset Class for K-Fold Cross-Validation
# ----------------------
class SubsetWithTransform(Dataset):
    """
    Wrapper class that allows us to apply different transforms
    to subsets of the main dataset during cross-validation.
    """
    def __init__(self, dataset, indices, transform=None):
        """
        Args:
            dataset: The full ImageFolder dataset.
            indices: List of indices for this subset (train or test).
            transform: Preprocessing transforms to apply to the images.
        """
        self.dataset = dataset
        self.indices = indices
        self.transform = transform

    def __len__(self):
        """Return the number of images in this subset."""
        return len(self.indices)

    def __getitem__(self, idx):
        """
        Get one image and its label from the subset.
        Args:
            idx: Index within this subset (0 to len(subset)-1).
        Returns:
            img: Preprocessed image tensor.
            label: Class label (0 or 1).
        """
        real_idx = self.indices[idx] # Convert subset index to full dataset index
        img, label = self.dataset[real_idx] # Get original image and label
        if self.transform:
            img = self.transform(img) # Apply preprocessing transforms
        return img, label

# ----------------------
# Training and Validation Functions
# ----------------------
def train_epoch(model, dataloader, criterion, optimizer):
    """Train the model for one epoch (one pass through all training data)."""
    model.train() # Put model in training mode

    # Initialize tracking variables
    total_loss = 0.0
    correct_predictions = 0
    total_samples = 0

    # Process each batch of images
    for batch_inputs, batch_labels in dataloader:
        # Move data to GPU/MPS if available
        batch_inputs = batch_inputs.to(device)
        batch_labels = batch_labels.to(device)

        # Reset gradients from previous batch
        optimizer.zero_grad()

        # Forward pass: get model predictions
        predictions = model(batch_inputs)

        # Calculate loss (how wrong the predictions are)
        loss = criterion(predictions, batch_labels)

        # Backward pass: calculate gradients
        loss.backward()

        # Update the model weights based on gradients
        optimizer.step()

        # Track statistics for this batch
        total_loss += loss.item() * batch_inputs.size(0)
        predicted_classes = predictions.argmax(1) # Get class with highest probability
        correct_predictions += (predicted_classes == batch_labels).sum().item()
        total_samples += batch_labels.size(0)

    # Calculate average loss and accuracy for the epoch
    avg_loss = total_loss / total_samples
    accuracy = correct_predictions / total_samples
    return avg_loss, accuracy

def validate_epoch(model, dataloader, criterion):
    """Evaluate the model on test data (no training)."""
    model.eval() # Put model in evaluation mode

    # Initialize tracking variables
    total_loss = 0.0
    correct_predictions = 0
    total_samples = 0

    # Disable gradient calculations for faster inference
    with torch.no_grad():
        for batch_inputs, batch_labels in dataloader:
            # Move data to GPU/MPS if available
            batch_inputs = batch_inputs.to(device)
            batch_labels = batch_labels.to(device)

            # Get model predictions
            predictions = model(batch_inputs)

            # Calculate loss
            loss = criterion(predictions, batch_labels)

            # Track statistics
            total_loss += loss.item() * batch_inputs.size(0)
            predicted_classes = predictions.argmax(1)
            correct_predictions += (predicted_classes == batch_labels).sum().item()
            total_samples += batch_labels.size(0)

    # Calculate average loss and accuracy
    avg_loss = total_loss / total_samples
    accuracy = correct_predictions / total_samples
    return avg_loss, accuracy

# ----------------------
# Load and Explore Dataset
# ----------------------
print("📁 Loading cricket ball dataset...")
full_dataset = datasets.ImageFolder(dataset_dir)  # Load images from folder structure
class_names = full_dataset.classes  # Get class names from folder names
print(f"✅ Found {len(full_dataset)} total images")
print(f"📊 Classes: {class_names}")
print(f"📊 Images per class: {[full_dataset.targets.count(i) for i in range(len(class_names))]}")

# ----------------------
# K-Fold Cross-Validation Training
# ----------------------
print(f"\n🔄 Starting {k_folds}-fold cross-validation...")

# Create k-fold splitter that shuffles data and splits into k groups
kfold = KFold(n_splits=k_folds, shuffle=True, random_state=42)
fold_results = []  # Store accuracy results for each fold

# Train and test on each fold
for fold_number, (train_indices, test_indices) in enumerate(kfold.split(full_dataset)):
    print(f"\n📂 Training Fold {fold_number + 1}/{k_folds}")
    print(f"   📈 Training samples: {len(train_indices)}")
    print(f"   📊 Testing samples: {len(test_indices)}")

    # Create datasets for this fold
    train_subset = SubsetWithTransform(full_dataset, train_indices, transform=train_transform)
    test_subset = SubsetWithTransform(full_dataset, test_indices, transform=test_transform)
    
    # Create data loaders (handle batching and shuffling)
    train_loader = DataLoader(train_subset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_subset, batch_size=batch_size, shuffle=False)

    # ----------------------
    # Model Setup for This Fold
    # ----------------------
    print("   🧠 Setting up ResNet18 model...")
    
    # Load pretrained ResNet18 (trained on ImageNet)
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    
    # Freeze fewer layers (unfreeze last ResNet block)
    for name, param in model.named_parameters():
        if 'layer4' in name or 'fc' in name:  # Unfreeze layer4 and fc
            param.requires_grad = True
        else:
            param.requires_grad = False

    model.fc = nn.Sequential(
        nn.Dropout(0.5),  # Add dropout before final layer
        nn.Linear(model.fc.in_features, num_classes)
    )
    
    # Move model to GPU/MPS if available
    model = model.to(device)

    # ----------------------
    # Training Setup
    # ----------------------
    # Loss function: measures how wrong predictions are
    criterion = nn.CrossEntropyLoss()
    
    # Optimizer: updates model weights
    optimizer = torch.optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()), 
        lr=learning_rate, 
        weight_decay=0.01  # L2 regularization
    )
    
    # Learning rate scheduler
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='max', factor=0.5, patience=3
    )

    # ----------------------
    # Training loop with early stopping
    # ----------------------
    best_test_accuracy = 0.0
    patience = 5
    patience_counter = 0

    for epoch in range(num_epochs):
        print(f"   🔄 Epoch {epoch+1}/{num_epochs}")
        
        train_loss, train_accuracy = train_epoch(model, train_loader, criterion, optimizer)
        test_loss, test_accuracy = validate_epoch(model, test_loader, criterion)
        
        print(f"      📈 Train: Loss={train_loss:.4f}, Acc={train_accuracy:.4f}")
        print(f"      📊 Test:  Loss={test_loss:.4f}, Acc={test_accuracy:.4f}")
        
        if test_accuracy > best_test_accuracy:
            best_test_accuracy = test_accuracy
            model_filename = os.path.join(models_dir, f"model_{fold_number+1}.pth")
            torch.save(model.state_dict(), model_filename)
            print(f"      💾 New best model saved: {model_filename}")
            patience_counter = 0
        else:
            patience_counter += 1
            
        if patience_counter >= patience:
            print(f"      🛑 Early stopping at epoch {epoch+1}")
            break
        
        scheduler.step(test_accuracy)

    print(f"   ✅ Best accuracy for fold {fold_number+1}: {best_test_accuracy:.4f}")
    fold_results.append(best_test_accuracy)

# ----------------------
# Final Results Summary
# ----------------------
print("\n" + "="*50)
print("📊 CROSS-VALIDATION RESULTS SUMMARY")
print("="*50)

for fold_idx, accuracy in enumerate(fold_results):
    print(f"   Fold {fold_idx+1}: {accuracy:.4f} ({accuracy*100:.2f}%)")

average_accuracy = np.mean(fold_results)
std_accuracy = np.std(fold_results)

print("-"*50)
print(f"   📊 Average Accuracy: {average_accuracy:.4f} ({average_accuracy*100:.2f}%)")
print(f"   📊 Standard Deviation: {std_accuracy:.4f}")
print(f"   📊 Best Fold: {max(fold_results):.4f}")
print(f"   📊 Worst Fold: {min(fold_results):.4f}")
print("="*50)