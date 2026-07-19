#!/bin/bash

set -e

echo "Installing Python packages..."
pip install -r requirements.txt

echo "Installing PyInstaller..."
pip install pyinstaller

echo "Cleaning previous builds..."
rm -rf build
rm -rf dist

echo "Building..."

pyinstaller UniversalVideoDownloader.spec

echo "Done!"