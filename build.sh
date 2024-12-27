#!/usr/bin/env bash
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Download and setup Chrome and ChromeDriver
mkdir -p $HOME/chrome
cd $HOME/chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -x google-chrome-stable_current_amd64.deb $HOME/chrome
export CHROME_PATH=$HOME/chrome/usr/bin/google-chrome

# Download compatible ChromeDriver
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | awk -F'.' '{print $1}')
wget -q "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}" -O chrome_version
CHROMEDRIVER_VERSION=$(cat chrome_version)
wget -q "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip chromedriver_linux64.zip
chmod +x chromedriver
export CHROMEDRIVER_PATH=$HOME/chrome/chromedriver 