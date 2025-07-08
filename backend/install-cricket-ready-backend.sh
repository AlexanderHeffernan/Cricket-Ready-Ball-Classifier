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

# Set install directory
INSTALL_DIR="$HOME/Cricket-Ready-Backend"
CERTS_DIR="$INSTALL_DIR/certs"
mkdir -p "$INSTALL_DIR"
mkdir -p "$CERTS_DIR"
cd "$INSTALL_DIR"

# Download the pre-built binary
echo "Downloading Cricket-Ready Ball Classifier Backend binary..."
curl -sSL -o Cricket-Ready-Backend https://raw.githubusercontent.com/AlexanderHeffernan/Cricket-Ready-Ball-Classifier/main/backend/bin/Cricket-Ready-Backend
chmod +x Cricket-Ready-Backend

# Generate unique self-signed certificate and key
if [ ! -f "$CERTS_DIR/cricket-ready.crt" ] || [ ! -f "$CERTS_DIR/cricket-ready.key" ]; then
    echo "Generating self-signed certificate and key..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$CERTS_DIR/cricket-ready.key" \
        -out "$CERTS_DIR/cricket-ready.crt" \
        -subj "/C=US/ST=YourState/L=YourCity/O=Cricket-Ready-Ball-Classifier/OU=Back-end/CN=$(hostname)" \
        -addext "subjectAltName=DNS:$(hostname)"
    chmod 600 "$CERTS_DIR/cricket-ready.crt" "$CERTS_DIR/cricket-ready.key"
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