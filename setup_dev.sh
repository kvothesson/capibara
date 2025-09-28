#!/bin/bash

# Capibara Development Setup Script

echo "🦫 Setting up Capibara development environment..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install in development mode
echo "Installing Capibara in development mode..."
pip install -e .

echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To test Capibara, run:"
echo "  python test_capibara.py"
echo ""
echo "To use the CLI, run:"
echo "  capibara --help"
