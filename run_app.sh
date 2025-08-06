#!/bin/bash

# Insider Trading Tracker - Startup Script

echo "📈 Starting Insider Trading Tracker..."
echo "======================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if requirements are installed
echo "🔍 Checking dependencies..."
if ! python3 -c "import streamlit, beautifulsoup4, requests, pandas, plotly" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
fi

# Run tests
echo "🧪 Running tests..."
python3 test_app.py

# Start the application
echo "🚀 Starting Streamlit application..."
echo "📱 The app will open in your browser at http://localhost:8501"
echo "🛑 Press Ctrl+C to stop the application"
echo ""

streamlit run app.py 