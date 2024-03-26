#!/bin/bash

# Upgrade Tesseract to 5+ on Ubuntu

# Update the system
sudo apt-get update -y

# Install essential build tools
sudo apt-get install -y build-essential

# Remove older version of Tesseract, if installed
sudo apt-get remove --purge tesseract-ocr* -y

# Install required dependencies
sudo apt-get install g++ automake ca-certificates gnupg libleptonica-dev pkg-config libtool git -y

# Clone the Tesseract GitHub repository
git clone https://github.com/tesseract-ocr/tesseract.git

# Navigate to the Tesseract directory and compile
cd tesseract
./autogen.sh
./configure
make

# Install Tesseract
sudo make install

# Set the TESSDATA_PREFIX environment variable
echo "export TESSDATA_PREFIX=/usr/local/share/" >> ~/.bashrc
source ~/.bashrc

# Download Tesseract language data for English
# Update this URL if it changes in the future
#sudo wget -P /usr/local/share/tessdata/ https://github.com/tesseract-ocr/tessdata_best/raw/main/eng.traineddata
sudo wget -P /usr/local/share/tessdata/ https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata

# Check the installed version of Tesseract
tesseract --version

echo "Installation completed!"

