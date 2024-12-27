#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Chrome
CHROME_VERSION="114.0.5735.90-1"
wget -q "https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb"

# Add Chrome's repository key
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -

# Install dependencies
apt-get update
apt-get install -y \
    ./google-chrome-stable_${CHROME_VERSION}_amd64.deb \
    unzip \
    xvfb \
    libxi6 \
    libgconf-2-4

rm google-chrome-stable_${CHROME_VERSION}_amd64.deb

# Install ChromeDriver
CHROMEDRIVER_VERSION="114.0.5735.90"
wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip -o chromedriver_linux64.zip
chmod +x chromedriver
mv chromedriver /usr/local/bin/
rm chromedriver_linux64.zip

# Create chrome directories if they don't exist
mkdir -p /usr/local/share/chrome
mkdir -p /usr/local/share/chrome/chromedriver

# Set permissions
chmod -R 777 /usr/local/share/chrome
chmod -R 777 /usr/local/bin/chromedriver

# Install Python dependencies
pip install -r requirements.txt 