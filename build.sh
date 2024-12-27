#!/usr/bin/env bash
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Create chrome directory
mkdir -p $HOME/chrome
cd $HOME/chrome

# Download Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -x google-chrome-stable_current_amd64.deb $HOME/chrome

# Set Chrome path
CHROME_PATH=$HOME/chrome/usr/bin/google-chrome

# Use a specific ChromeDriver version (you can update this version as needed)
CHROMEDRIVER_VERSION="114.0.5735.90"  # Use a stable version
wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip chromedriver_linux64.zip
chmod +x chromedriver

# Export paths
export CHROME_PATH=$HOME/chrome/usr/bin/google-chrome
export CHROMEDRIVER_PATH=$HOME/chrome/chromedriver

# Print versions for debugging
echo "Chrome path: $CHROME_PATH"
echo "ChromeDriver path: $CHROMEDRIVER_PATH" 