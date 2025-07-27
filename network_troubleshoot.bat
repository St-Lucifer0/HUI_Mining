@echo off
echo ========================================
echo Network Troubleshooting for Federated System
echo ========================================
echo.

REM Get current IP address
echo [1] Current Network Configuration:
echo ----------------------------------------
ipconfig | findstr /i "IPv4"
echo.

REM Test network connectivity
echo [2] Testing Network Connectivity:
echo ----------------------------------------
set /p TARGET_IP="Enter the IP address to test (e.g., 192.168.1.100): "

echo Testing ping to %TARGET_IP%...
ping -n 4 %TARGET_IP%

if errorlevel 1 (
    echo.
    echo [ERROR] Ping failed! Possible issues:
    echo - Devices not on same network
    echo - Windows Firewall blocking
    echo - Target device offline
    echo - Router/network configuration issue
    echo.
) else (
    echo.
    echo [SUCCESS] Ping successful!
    echo.
)

REM Test specific ports
echo [3] Testing Port Connectivity:
echo ----------------------------------------
echo Testing port 5000 (API Server)...
telnet %TARGET_IP% 5000 2>nul
if errorlevel 1 (
    echo Port 5000 is not accessible
) else (
    echo Port 5000 is accessible
)

echo Testing port 50051 (Federated Server)...
telnet %TARGET_IP% 50051 2>nul
if errorlevel 1 (
    echo Port 50051 is not accessible
) else (
    echo Port 50051 is accessible
)

echo.
echo [4] Firewall Configuration:
echo ----------------------------------------
echo To allow ports through Windows Firewall:
echo 1. Open Windows Defender Firewall
echo 2. Click "Advanced settings"
echo 3. Create Inbound Rules for:
echo    - Port 5000 (TCP)
echo    - Port 50051 (TCP)
echo.

echo [5] Network Diagnostics:
echo ----------------------------------------
echo Current network adapters:
ipconfig /all | findstr /i "adapter\|IPv4\|subnet"
echo.

echo [6] Recommendations:
echo ----------------------------------------
if errorlevel 1 (
    echo - Ensure both laptops are connected to the same WiFi network
    echo - Check if Windows Firewall is blocking the connection
    echo - Verify the server is actually running on the target IP
    echo - Try disabling Windows Firewall temporarily for testing
    echo - Check router settings for device isolation
)

echo.
pause
