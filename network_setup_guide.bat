@echo off
echo ========================================
echo FEDERATED SYSTEM NETWORK SETUP GUIDE
echo ========================================
echo.
echo This script will help you connect both laptops to the same network
echo and establish proper connectivity for the federated system.
echo.

echo STEP 1: CHECK CURRENT NETWORK STATUS
echo =====================================
echo Your current network information:
echo.
ipconfig | findstr /C:"IPv4 Address" /C:"Subnet Mask" /C:"Default Gateway"
echo.
netsh wlan show profiles
echo.

echo STEP 2: NETWORK CONNECTIVITY ANALYSIS
echo =====================================
echo Current client IP: 192.168.137.160 (subnet 192.168.137.x)
echo Target server IP: 192.168.1.100 (subnet 192.168.1.x)
echo.
echo [PROBLEM IDENTIFIED] You are on DIFFERENT network subnets!
echo This is why ping fails with 100%% packet loss.
echo.

echo STEP 3: SOLUTIONS TO TRY
echo ========================
echo.
echo OPTION A: Connect to Same Wi-Fi Network (RECOMMENDED)
echo -----------------------------------------------------
echo 1. On the SERVER laptop, check which Wi-Fi network it's connected to
echo 2. Connect THIS laptop to the SAME Wi-Fi network
echo 3. Get the server's actual IP address from the server laptop
echo.
echo OPTION B: Use Server's Actual IP on Current Network
echo --------------------------------------------------
echo If the server is actually on your network (192.168.137.x), 
echo the IP 192.168.1.100 might be incorrect.
echo.

echo STEP 4: NETWORK DISCOVERY
echo =========================
echo Let's scan for devices on your current network...
echo.
for /L %%i in (1,1,254) do (
    ping -n 1 -w 100 192.168.137.%%i >nul 2>&1
    if not errorlevel 1 echo Found device: 192.168.137.%%i
)
echo.
echo Network scan complete. Any devices found above might be your server.
echo.

echo STEP 5: FIREWALL CONFIGURATION
echo ==============================
echo Adding firewall rules for the federated system...
echo.
netsh advfirewall firewall add rule name="HUI Mining API" dir=in action=allow protocol=TCP localport=5000 >nul 2>&1
netsh advfirewall firewall add rule name="HUI Mining Federated" dir=in action=allow protocol=TCP localport=50051 >nul 2>&1
netsh advfirewall firewall add rule name="ICMP Ping" protocol=icmpv4:8,any dir=in action=allow >nul 2>&1
echo Firewall rules added successfully.
echo.

echo STEP 6: TEST CONNECTIVITY
echo =========================
set /p TEST_IP="Enter the server IP to test (or press Enter to skip): "
if not "%TEST_IP%"=="" (
    echo Testing ping to %TEST_IP%...
    ping -n 2 %TEST_IP%
    echo.
    echo Testing port connectivity...
    powershell -Command "Test-NetConnection -ComputerName %TEST_IP% -Port 5000 -InformationLevel Quiet" >nul 2>&1
    if not errorlevel 1 (
        echo [OK] Port 5000: REACHABLE
    ) else (
        echo [ERROR] Port 5000: NOT REACHABLE
    )
    
    powershell -Command "Test-NetConnection -ComputerName %TEST_IP% -Port 50051 -InformationLevel Quiet" >nul 2>&1
    if not errorlevel 1 (
        echo [OK] Port 50051: REACHABLE
    ) else (
        echo [ERROR] Port 50051: NOT REACHABLE
    )
)

echo.
echo ========================================
echo NEXT STEPS
echo ========================================
echo.
echo 1. ENSURE SAME NETWORK:
echo    - Check Wi-Fi network on server laptop
echo    - Connect this laptop to the SAME network
echo    - Get correct server IP address
echo.
echo 2. UPDATE SERVER IP:
echo    - Use the correct server IP in your client connection
echo    - The IP should be 192.168.137.x if on same network
echo.
echo 3. START THE SYSTEM:
echo    - Run server: start_integrated_server.bat
echo    - Run client: start_integrated_client.bat
echo.
echo 4. IF STILL NOT WORKING:
echo    - Try temporarily disabling Windows Firewall
echo    - Check antivirus software settings
echo    - Restart both laptops and network equipment
echo.
pause
