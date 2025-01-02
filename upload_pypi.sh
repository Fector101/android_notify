#!/bin/bash

# Load environment variables from .env file (if it exists)
PARENT_DIR=$(dirname "$(pwd)")
ENV_FILE="$PARENT_DIR/.env"
echo "The env file: $ENV_FILE"

if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

# Ensure we are in the root directory of the package (where setup.py is located)
PACKAGE_DIR=$(pwd)
echo "The current working directory is: $PACKAGE_DIR"

# Step 1: Clean previous builds (if any)
echo "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info

# Step 2: Build the package
echo "Building the package..."
python3 setup.py sdist bdist_wheel

# Step 3: Upload to PyPI using twine
echo "Uploading the package to PyPI..."
twine upload dist/* --verbose

# Step 4: Clean up the build directories
echo "Cleaning up build files..."
rm -rf dist/ build/ *.egg-info

echo "Script for Upload done!"