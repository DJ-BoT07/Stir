#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Chrome
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
apt-get update
apt-get install -y google-chrome-stable

# Install Python dependencies
pip install -r requirements.txt

# Additional commands for Chrome/Selenium setup can go here 