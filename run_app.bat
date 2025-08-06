@echo off

REM Insider Trading Tracker - Startup Script for Windows

echo 📈 Starting Insider Trading Tracker...
echo ======================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if requirements are installed
echo 🔍 Checking dependencies...
python -c "import streamlit, beautifulsoup4, requests, pandas, plotly" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing dependencies...
    pip install -r requirements.txt
)

REM Run tests
echo 🧪 Running tests...
python test_app.py

REM Start the application
echo 🚀 Starting Streamlit application...
echo 📱 The app will open in your browser at http://localhost:8501
echo 🛑 Press Ctrl+C to stop the application
echo.

streamlit run app.py

pause 