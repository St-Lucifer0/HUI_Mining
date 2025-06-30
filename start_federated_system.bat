@echo off
echo Starting Federated Learning System for High-Utility Itemset Mining
echo ================================================================

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: docker-compose is not available. Please install Docker Compose.
    pause
    exit /b 1
)

echo Building Docker images...
python run_federated_system.py build
if %errorlevel% neq 0 (
    echo Error: Failed to build Docker images.
    pause
    exit /b 1
)

echo Starting federated learning system...
python run_federated_system.py start
if %errorlevel% neq 0 (
    echo Error: Failed to start the system.
    pause
    exit /b 1
)

echo.
echo Federated Learning System is starting up...
echo.
echo Services:
echo - Server: http://localhost:50051 (gRPC)
echo - Monitoring: http://localhost:8080 (HTTP)
echo.
echo To view logs: python run_federated_system.py logs --follow
echo To stop system: python run_federated_system.py stop
echo To check status: python run_federated_system.py status
echo.
echo Press any key to continue...
pause >nul

echo.
echo Checking system status...
python run_federated_system.py status

echo.
echo System is ready! You can now run clients or monitor the system.
pause 