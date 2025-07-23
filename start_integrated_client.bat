@echo off
echo ========================================
echo Starting Integrated FP-Growth System
echo Mode: CLIENT
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

REM Get server address from user
set /p SERVER_ADDRESS="Enter server IP address (e.g., 192.168.1.100): "

REM Get client ID from user
set /p CLIENT_ID="Enter client ID (e.g., client-4): "

REM Start the integrated client
echo Starting integrated client...
echo Client ID: %CLIENT_ID%
echo Connecting to server: %SERVER_ADDRESS%:50051
echo.
echo Press Ctrl+C to stop the client
echo.

python integrated_system.py --mode client --client-id %CLIENT_ID% --server-address %SERVER_ADDRESS% --federated-port 50051

pause 