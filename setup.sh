#!/bin/bash
# CareerLaunch AI Backend - Linux/Mac Setup Script

echo ""
echo "====================================="
echo "CareerLaunch AI Backend - Setup"
echo "====================================="
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.11+ from https://python.org"
    exit 1
fi

echo "Python version: $(python3 --version)"

# Create virtual environment
echo ""
echo "[1/5] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "[2/5] Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "[3/5] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

# Create environment file
echo "[4/5] Creating environment configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file. Please edit it with your configuration."
else
    echo ".env file already exists"
fi

# Verify installation
echo "[5/5] Verifying installation..."
python -c "import fastapi; import sqlalchemy; import pydantic; print('✓ All dependencies installed successfully')"
if [ $? -ne 0 ]; then
    echo "ERROR: Dependency verification failed"
    exit 1
fi

echo ""
echo "====================================="
echo "Setup Complete!"
echo "====================================="
echo ""
echo "Next steps:"
echo "1. Edit the .env file with your configuration"
echo "2. Run: python app/main.py"
echo "3. Visit: http://localhost:8000/docs"
echo ""
echo "For Docker setup, run: docker-compose up -d"
echo ""
echo "Activate the virtual environment with:"
echo "  source venv/bin/activate (Linux/Mac)"
echo ""
