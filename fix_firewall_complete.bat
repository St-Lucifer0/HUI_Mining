@echo off
echo ========================================
echo COMPREHENSIVE FIREWALL FIX SCRIPT
echo ========================================
echo.

echo [1] Current network configuration:
ipconfig | findstr "IPv4"
echo.

echo [2] Adding Windows Firewall rules...
echo Adding inbound rules for HUI Mining System...

REM Add inbound rules for both TCP and UDP
netsh advfirewall firewall add rule name="HUI Mining API Server TCP" dir=in action=allow protocol=TCP localport=5000
netsh advfirewall firewall add rule name="HUI Mining Federated Server TCP" dir=in action=allow protocol=TCP localport=50051
netsh advfirewall firewall add rule name="HUI Mining API Server UDP" dir=in action=allow protocol=UDP localport=5000
netsh advfirewall firewall add rule name="HUI Mining Federated Server UDP" dir=in action=allow protocol=UDP localport=50051

echo Adding outbound rules for HUI Mining System...
netsh advfirewall firewall add rule name="HUI Mining API Client TCP Out" dir=out action=allow protocol=TCP localport=5000
netsh advfirewall firewall add rule name="HUI Mining Federated Client TCP Out" dir=out action=allow protocol=TCP localport=50051
netsh advfirewall firewall add rule name="HUI Mining API Client UDP Out" dir=out action=allow protocol=UDP localport=5000
netsh advfirewall firewall add rule name="HUI Mining Federated Client UDP Out" dir=out action=allow protocol=UDP localport=50051

echo Adding Python application rules...
netsh advfirewall firewall add rule name="Python HUI Mining" dir=in action=allow program="%PYTHON_EXE%" enable=yes
netsh advfirewall firewall add rule name="Python HUI Mining Out" dir=out action=allow program="%PYTHON_EXE%" enable=yes

echo.
echo [3] Enabling ICMP (ping) through firewall...
netsh advfirewall firewall add rule name="ICMP Allow incoming V4 echo request" protocol=icmpv4:8,any dir=in action=allow

echo.
echo [4] Setting network profile to Private (more permissive)...
powershell -Command "Set-NetConnectionProfile -NetworkCategory Private"

echo.
echo [5] Temporarily disabling Windows Firewall for testing (CAUTION!)...
echo WARNING: This will temporarily disable Windows Firewall
set /p DISABLE_FW="Disable Windows Firewall temporarily for testing? (y/N): "
if /i "%DISABLE_FW%"=="y" (
    netsh advfirewall set allprofiles state off
    echo Windows Firewall DISABLED temporarily
    echo Remember to re-enable it later with: netsh advfirewall set allprofiles state on
) else (
    echo Windows Firewall remains enabled
)

echo.
echo [6] Testing network connectivity...
set /p SERVER_IP="Enter server IP to test (e.g., 192.168.1.100): "
if not "%SERVER_IP%"=="" (
    echo Testing ping to %SERVER_IP%...
    ping -n 2 %SERVER_IP%
    
    echo.
    echo Testing telnet to %SERVER_IP%:5000...
    powershell -Command "Test-NetConnection -ComputerName %SERVER_IP% -Port 5000"
    
    echo.
    echo Testing telnet to %SERVER_IP%:50051...
    powershell -Command "Test-NetConnection -ComputerName %SERVER_IP% -Port 50051"
)

echo.
echo ========================================
echo FIREWALL CONFIGURATION COMPLETE
echo ========================================
echo.
echo Next steps:
echo 1. Ensure both laptops are on the same network
echo 2. Run this script on BOTH client and server laptops
echo 3. If still not working, check router/network settings
echo 4. Consider using the server's actual IP address
echo.
echo To re-enable Windows Firewall later:
echo netsh advfirewall set allprofiles state on
echo.
pause
