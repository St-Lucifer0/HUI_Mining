@echo off
echo.
echo ========================================
echo    FP-GROWTH FEDERATED LEARNING UI
echo ========================================
echo.

echo Choose an interface option:
echo 1. Interactive Dashboard (Advanced)
echo 2. Run Mining with Website
echo 3. Performance Monitor
echo 4. All UIs (Dashboard + Performance Monitor)
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo Starting Interactive Dashboard...
    python dashboard.py --host 0.0.0.0 --port 8050
) else if "%choice%"=="2" (
    echo Running HUI Mining with Website...
    python run_hui_mining_and_website.py
) else if "%choice%"=="3" (
    echo Starting Performance Monitor...
    python performance_monitor.py
) else if "%choice%"=="4" (
    echo Starting all UI components...
    start python dashboard.py --host 0.0.0.0 --port 8050
    timeout /t 3 /nobreak >nul
    start python performance_monitor.py
    echo.
    echo 🌐 Dashboard: http://localhost:8050
) else (
    echo Invalid choice. Please run the script again.
)

echo.
echo Press any key to exit...
pause >nul 