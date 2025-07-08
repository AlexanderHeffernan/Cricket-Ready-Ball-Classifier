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

# Set install directory
INSTALL_DIR="$HOME/Cricket-Ready-Backend"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Download the pre-built binary
echo "Downloading Cricket-Ready Ball Classifier Backend binary..."
curl -sSL -o Cricket-Ready-Backend https://raw.githubusercontent.com/AlexanderHeffernan/Cricket-Ready-Ball-Classifier/main/backend/bin/Cricket-Ready-Backend
chmod +x Cricket-Ready-Backend

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

# Download requirements.txt if it exists
echo "Downloading requirements.txt..."
curl -sSL -o requirements.txt https://raw.githubusercontent.com/AlexanderHeffernan/Cricket-Ready-Ball-Classifier/main/backend/nn-classifier/requirements.txt || {
    echo -e "${YELLOW}No requirements.txt found, creating one with basic dependencies...${NC}"
    cat > requirements.txt <<EOF
torch
torchvision
pillow
EOF
}

# Set up Python virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment and install packages
echo "Installing Python packages..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

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

[Install]
WantedBy=multi-user.target
EOL

# Reload and enable service
sudo systemctl daemon-reload
sudo systemctl enable cricket-ready-backend.service
sudo systemctl start cricket-ready-backend.service

# Verify it's running
if sudo systemctl is-active cricket-ready-backend.service >/dev/null; then
    echo -e "${GREEN}Cricket-Ready Ball Classifier Backend installed and running at https://$(hostname):49160/predict${NC}"
else
    echo -e "${RED}Failed to start Cricket-Ready Ball Classifier Backend. Check logs with 'journalctl -u cricket-ready-backend.service'${NC}"
    exit 1
fi