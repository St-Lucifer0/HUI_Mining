@echo off
echo ========================================
echo Federated Learning Client Setup
echo ========================================

echo.
echo This script will set up and start a federated learning client.
echo Make sure the server is running first.
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
echo Client Configuration
echo ========================================
echo.

set /p CLIENT_ID="Enter client ID (e.g., client-1): "
set /p SERVER_IP="Enter server IP address: "
set /p DATASET_PATH="Enter dataset path (or press Enter for sample data): "

echo.
echo Starting client with:
echo Client ID: %CLIENT_ID%
echo Server: %SERVER_IP%:50051
if not "%DATASET_PATH%"=="" echo Dataset: %DATASET_PATH%
echo.

if "%DATASET_PATH%"=="" (
    python setup_client.py --client-id %CLIENT_ID% --server-address %SERVER_IP%
) else (
    python setup_client.py --client-id %CLIENT_ID% --server-address %SERVER_IP% --dataset-path "%DATASET_PATH%"
)

echo.
echo Client stopped.
pause 