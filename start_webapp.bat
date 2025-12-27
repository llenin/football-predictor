@echo off
REM NFL Predictor - Web App Launcher (Windows)

echo.
echo ======================================================================
echo   NFL Game Outcome Predictor - Web Application
echo ======================================================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then install dependencies: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if model exists
if not exist "models\logistic_regression.pkl" (
    echo.
    echo WARNING: Model not trained yet!
    echo Training model now... this may take a minute...
    echo.
    python src\train_model.py
    if errorlevel 1 (
        echo.
        echo ERROR: Model training failed!
        echo Please ensure data files are present in data\processed\
        pause
        exit /b 1
    )
)

echo.
echo Starting web server...
echo.
echo ======================================================================
echo   Web App will open at: http://localhost:8000
echo   API Documentation at: http://localhost:8000/docs
echo   Press Ctrl+C to stop the server
echo ======================================================================
echo.

REM Start the server
uvicorn backend.app:app --reload

pause
