#!/bin/bash
# NFL Predictor - Web App Launcher (Mac/Linux)

echo ""
echo "======================================================================"
echo "  NFL Game Outcome Predictor - Web Application"
echo "======================================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run: python -m venv venv"
    echo "Then install dependencies: pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if model exists
if [ ! -f "models/logistic_regression.pkl" ]; then
    echo ""
    echo "WARNING: Model not trained yet!"
    echo "Training model now... this may take a minute..."
    echo ""
    python src/train_model.py
    if [ $? -ne 0 ]; then
        echo ""
        echo "ERROR: Model training failed!"
        echo "Please ensure data files are present in data/processed/"
        exit 1
    fi
fi

echo ""
echo "Starting web server..."
echo ""
echo "======================================================================"
echo "  Web App will open at: http://localhost:8000"
echo "  API Documentation at: http://localhost:8000/docs"
echo "  Press Ctrl+C to stop the server"
echo "======================================================================"
echo ""

# Start the server
uvicorn backend.app:app --reload
