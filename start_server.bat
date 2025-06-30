@echo off
echo ========================================
echo Federated Learning Server Setup
echo ========================================

echo.
echo This script will set up and start the federated learning server.
echo Make sure all clients are ready to connect.
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo Error: requirements.txt not found
    pause
    exit /b 1
)

echo Installing dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo Generating gRPC code...
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. federated_learning.proto
if %errorlevel% neq 0 (
    echo Error: Failed to generate gRPC code
    pause
    exit /b 1
)

echo.
echo ========================================
echo Starting Federated Learning Server
echo ========================================
echo.
echo The server will start on port 50051
echo Clients should connect to this machine's IP address
echo.
echo Press Ctrl+C to stop the server
echo.

python setup_server.py

echo.
echo Server stopped.
pause 