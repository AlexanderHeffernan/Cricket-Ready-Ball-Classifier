#!/bin/bash

# Exit on any error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Cricket-Ready Ball Classifier Backend installation...${NC}"

# Check for required tools
command -v curl >/dev/null 2>&1 || { echo -e "${RED}curl is required. Please install it (e.g., 'sudo apt install curl').${NC}"; exit 1; }
command -v openssl >/dev/null 2>&1 || { echo -e "${RED}OpenSSL is required. Please install it (e.g., 'sudo apt install openssl').${NC}"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo -e "${RED}Python 3 is required. Please install it (e.g., 'sudo apt install python3').${NC}"; exit 1; }
command -v cargo >/dev/null 2>&1 || { echo "Rust/Cargo is required to build the hardened backend; the legacy prebuilt binary is unsupported."; exit 1; }
python3 -c 'import sys; assert sys.version_info >= (3, 11), "Python >=3.11 is required for Pillow 13"'

# Set install directory
INSTALL_DIR="$HOME/Cricket-Ready-Backend"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Build the hardened sources rather than installing the stale checked-in binary.
echo "Building Cricket-Ready Ball Classifier Backend (requires a current Rust toolchain and OpenSSL development headers)..."
mkdir -p src training_data/pending
for file in Cargo.toml Cargo.lock src/main.rs; do
    curl -fsSL -o "$file" "https://raw.githubusercontent.com/AlexanderHeffernan/Cricket-Ready-Ball-Classifier/main/backend/$file"
done
cargo build --release --locked
install -m 755 target/release/Cricket-Ready-Backend Cricket-Ready-Backend

# Create nn-classifier directory and download predict.py
echo "Setting up neural network classifier..."
mkdir -p nn-classifier
cd nn-classifier

echo "Downloading predict.py script..."
curl -sSL -o predict.py https://raw.githubusercontent.com/AlexanderHeffernan/Cricket-Ready-Ball-Classifier/main/backend/nn-classifier/predict.py

# Download models
echo "Downloading neural network models..."
mkdir -p models
cd models

echo "Downloading model_1.pth..."
curl -sSL -o model_1.pth https://raw.githubusercontent.com/AlexanderHeffernan/Cricket-Ready-Ball-Classifier/main/backend/nn-classifier/models/model_1.pth || {
    echo -e "${RED}Failed to download model_1.pth${NC}"
    exit 1
}

echo "Downloading model_2.pth..."
curl -sSL -o model_2.pth https://raw.githubusercontent.com/AlexanderHeffernan/Cricket-Ready-Ball-Classifier/main/backend/nn-classifier/models/model_2.pth || {
    echo -e "${RED}Failed to download model_2.pth${NC}"
    exit 1
}

echo "Downloading model_3.pth..."
curl -sSL -o model_3.pth https://raw.githubusercontent.com/AlexanderHeffernan/Cricket-Ready-Ball-Classifier/main/backend/nn-classifier/models/model_3.pth || {
    echo -e "${RED}Failed to download model_3.pth${NC}"
    exit 1
}

echo -e "${GREEN}All models downloaded successfully${NC}"

# Go back to nn-classifier directory
cd ..

# Fail closed instead of falling back to unconstrained dependency versions.
curl -fsSL -o requirements-inference.txt https://raw.githubusercontent.com/AlexanderHeffernan/Cricket-Ready-Ball-Classifier/main/backend/nn-classifier/requirements-inference.txt

# Set up Python virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment and install packages
echo "Installing Python packages..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-inference.txt

# Verify installation
echo "Verifying Python environment..."
python3 -c "import torch, torchvision, PIL; print('All packages installed successfully')" || {
    echo -e "${RED}Failed to verify Python package installation${NC}"
    exit 1
}

# Go back to main directory
cd "$INSTALL_DIR"

# Generate unique self-signed certificate and key
if [ ! -f "cricket-ready.crt" ] || [ ! -f "cricket-ready.key" ]; then
    echo "Generating self-signed certificate and key..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout cricket-ready.key \
        -out cricket-ready.crt \
        -subj "/C=US/ST=YourState/L=YourCity/O=Cricket-Ready-Ball-Classifier/OU=Back-end/CN=$(hostname)" \
        -addext "subjectAltName=DNS:$(hostname)"
    chmod 600 cricket-ready.crt cricket-ready.key
fi

# Set up systemd service
SERVICE_FILE="/etc/systemd/system/cricket-ready-backend.service"
echo "Configuring systemd service..."
sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Cricket-Ready Ball Classifier Backend
After=network.target

[Service]
ExecStart=$INSTALL_DIR/Cricket-Ready-Backend
WorkingDirectory=$INSTALL_DIR
Restart=always
User=$(whoami)
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=$INSTALL_DIR/training_data
MemoryMax=2G
TasksMax=64
CPUQuota=200%
UMask=0077

[Install]
WantedBy=multi-user.target
EOL

# Reload and enable service
sudo systemctl daemon-reload
sudo systemctl enable cricket-ready-backend.service
sudo systemctl start cricket-ready-backend.service

# Verify it's running
if sudo systemctl is-active cricket-ready-backend.service >/dev/null; then
    echo -e "${GREEN}Cricket-Ready Ball Classifier Backend installed and running at https://$(hostname):49161/predict${NC}"
else
    echo -e "${RED}Failed to start Cricket-Ready Ball Classifier Backend. Check logs with 'journalctl -u cricket-ready-backend.service'${NC}"
    exit 1
fi
