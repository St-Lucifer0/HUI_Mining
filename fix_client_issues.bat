@echo off
echo ========================================
echo FEDERATED SYSTEM CLIENT FIX SCRIPT
echo ========================================
echo.

echo [1] Checking Python version...
python --version
echo.

echo [2] Checking if we're in the right directory...
if exist "integrated_system.py" (
    echo ✅ integrated_system.py found
) else (
    echo ❌ integrated_system.py NOT found - you may be in the wrong directory
    echo Please navigate to the project directory first
    pause
    exit /b 1
)

echo.
echo [3] Running comprehensive diagnostic...
python diagnose_system.py
echo.

echo [4] Attempting to fix common issues...
echo.

echo [4a] Upgrading protobuf...
pip install --upgrade protobuf>=4.25.0

echo.
echo [4b] Reinstalling grpc packages...
pip install --upgrade grpcio grpcio-tools

echo.
echo [4c] Installing minimal requirements...
pip install -r requirements-minimal.txt

echo.
echo [5] Testing backend module imports...
python -c "
try:
    from google.protobuf import runtime_version
    print('✅ runtime_version import: SUCCESS')
except ImportError as e:
    print('❌ runtime_version import: FAILED -', e)

try:
    import federated_learning_pb2
    print('✅ federated_learning_pb2 import: SUCCESS')
except ImportError as e:
    print('❌ federated_learning_pb2 import: FAILED -', e)
"

echo.
echo [6] Configuring Windows Firewall...
echo Adding firewall rules for ports 5000 and 50051...
netsh advfirewall firewall add rule name="HUI Mining API Server" dir=in action=allow protocol=TCP localport=5000 >nul 2>&1
netsh advfirewall firewall add rule name="HUI Mining Federated Server" dir=in action=allow protocol=TCP localport=50051 >nul 2>&1
echo Firewall rules added (if you have admin privileges)

echo.
echo [7] Testing network connectivity...
set /p SERVER_IP="Enter server IP address (e.g., 192.168.1.100): "
echo Testing ping to %SERVER_IP%...
ping -n 2 %SERVER_IP%

echo.
echo ========================================
echo FIX SCRIPT COMPLETE
echo ========================================
echo.
echo Next steps:
echo 1. If Python version is 3.8, upgrade to Python 3.11+
echo 2. If ping fails, check network/firewall settings
echo 3. If imports still fail, try recreating virtual environment
echo.
pause
