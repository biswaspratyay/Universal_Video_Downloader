#!/bin/bash

set -e

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Cleaning previous builds..."
rm -rf build
rm -rf dist

echo "Building application..."
pyinstaller UniversalVideoDownloader.spec

echo "Build completed successfully!"