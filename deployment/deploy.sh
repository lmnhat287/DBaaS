#!/bin/bash

# Log function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Configuration
APP_DIR=/home/ubuntu/dbaas
VENV_DIR=$APP_DIR/venv

# Update system
log "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install dependencies
log "Installing required packages..."
sudo apt install -y python3-pip python3-venv nginx git

# Create application directory
log "Setting up application directory..."
mkdir -p $APP_DIR
cd $APP_DIR

# Clone repository
log "Cloning repository..."
git clone https://github.com/lmnhat287/DBaaS.git .

# Setup Python virtual environment
log "Setting up Python virtual environment..."
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate

# Install dependencies
log "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file
log "Creating environment file..."
sudo tee .env << EOF
SECRET_KEY=${SECRET_KEY}
MONGO_URI=${MONGO_URI}
FLASK_APP=run.py
FLASK_ENV=production
AWS_REGION=us-east-1
EOF