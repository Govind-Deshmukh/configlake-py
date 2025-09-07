#!/bin/bash
# ConfigLake Python Package Publishing Script

set -e

echo "🚀 Publishing ConfigLake Python Package"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/

# Build the package
echo "📦 Building package..."
python setup.py sdist bdist_wheel

# Check the build
echo "🔍 Checking package..."
twine check dist/*

# Ask user which repository to upload to
echo ""
echo "Choose publishing destination:"
echo "1) Test PyPI (recommended for testing)"
echo "2) Real PyPI (production)"
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        echo "📤 Uploading to Test PyPI..."
        twine upload --repository testpypi dist/*
        echo ""
        echo "✅ Package uploaded to Test PyPI!"
        echo "📥 Test installation with:"
        echo "pip install --index-url https://test.pypi.org/simple/ configlake"
        ;;
    2)
        echo "📤 Uploading to Real PyPI..."
        twine upload dist/*
        echo ""
        echo "✅ Package published to PyPI!"
        echo "📥 Install with: pip install configlake"
        echo "🔗 Package URL: https://pypi.org/project/configlake/"
        ;;
    *)
        echo "❌ Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "🎉 Publishing complete!"