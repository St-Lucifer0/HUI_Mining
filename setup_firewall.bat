@echo off
echo ========================================
echo Configuring Windows Firewall for Federated System
echo ========================================
echo.

echo This script will add firewall rules to allow:
echo - Port 5000 (API Server)
echo - Port 50051 (Federated Learning Server)
echo.

echo WARNING: This requires Administrator privileges
echo Please run this script as Administrator
echo.
pause

echo Adding firewall rule for port 5000...
netsh advfirewall firewall add rule name="HUI Mining API Server" dir=in action=allow protocol=TCP localport=5000

echo Adding firewall rule for port 50051...
netsh advfirewall firewall add rule name="HUI Mining Federated Server" dir=in action=allow protocol=TCP localport=50051

echo.
echo Firewall rules added successfully!
echo.

echo To remove these rules later, run:
echo netsh advfirewall firewall delete rule name="HUI Mining API Server"
echo netsh advfirewall firewall delete rule name="HUI Mining Federated Server"
echo.

pause
