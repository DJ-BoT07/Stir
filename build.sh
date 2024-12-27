#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Chrome
CHROME_VERSION="114.0.5735.90-1"
sudo wget -q "https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb"
sudo apt-get update
sudo apt-get install -y ./google-chrome-stable_${CHROME_VERSION}_amd64.deb
sudo rm google-chrome-stable_${CHROME_VERSION}_amd64.deb

# Install required dependencies
sudo apt-get install -y unzip xvfb libxi6 libgconf-2-4

# Install ChromeDriver
CHROMEDRIVER_VERSION="114.0.5735.90"
sudo wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
sudo unzip -o chromedriver_linux64.zip
sudo chmod +x chromedriver
sudo mv chromedriver /usr/local/bin/
sudo rm chromedriver_linux64.zip

# Create chrome directories if they don't exist
sudo mkdir -p /usr/local/share/chrome
sudo mkdir -p /usr/local/share/chrome/chromedriver

# Set permissions
sudo chmod -R 777 /usr/local/share/chrome
sudo chmod -R 777 /usr/local/bin/chromedriver

# Install Python dependencies
pip install -r requirements.txt 