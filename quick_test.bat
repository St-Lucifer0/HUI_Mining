@echo off
echo ========================================
echo Federated Learning System Quick Test
echo ========================================
echo.

echo Step 1: Generating gRPC code...
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. federated_learning.proto
if %errorlevel% neq 0 (
    echo ERROR: Failed to generate gRPC code
    echo Please install grpcio-tools: pip install grpcio-tools
    pause
    exit /b 1
)
echo ✓ gRPC code generated successfully
echo.

echo Step 2: Running system tests...
python test_federated_system.py
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Some tests failed, but continuing...
    echo.
)

echo Step 3: Testing network connectivity...
if "%1"=="" (
    echo Usage: quick_test.bat [server_ip]
    echo Example: quick_test.bat 172.20.10.14
    echo.
    echo Please provide the server IP address to test connectivity
    pause
    exit /b 1
)

echo Testing connection to %1:50051...
python network_troubleshooter.py %1 50051

echo.
echo ========================================
echo Quick test completed!
echo ========================================
echo.
echo Next steps:
echo 1. Start the server: python setup_server.py
echo 2. On other laptops, run: python setup_client.py --client-id client-1 --server-address %1
echo 3. If you have datasets: python setup_client.py --client-id client-1 --server-address %1 --dataset-path your_dataset.csv
echo.
pause 