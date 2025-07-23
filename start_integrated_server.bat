@echo off
echo ========================================
echo Starting Integrated FP-Growth System
echo Mode: SERVER
echo ========================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import flask, grpc, flask_cors, flask_socketio" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install flask flask-cors flask-socketio grpcio grpcio-tools
)

REM Start the integrated server
echo Starting integrated server...
echo API Server will be available at: http://localhost:5000
echo Federated Server will be available at: 0.0.0.0:50051
echo.
echo Press Ctrl+C to stop the server
echo.

python integrated_system.py --mode server --host 0.0.0.0 --api-port 5000 --federated-port 50051

pause 