@echo off
echo ========================================
echo FP-Growth Federated Learning Project Cleanup
echo ========================================
echo.

echo Removing redundant frontend files...
del /Q simple_frontend.html
del /Q script.js
rmdir /S /Q federated_ui_design_html

echo.
echo Removing duplicate dataset files...
del /Q client2_foodmart_dataset.csv
del /Q generated_foodmart_dataset.csv
del /Q generate_client2_dataset.py

echo.
echo Removing old configuration files...
del /Q server_config.json

echo.
echo Removing redundant documentation...
del /Q THRESHOLD_CONTROL_GUIDE.md
del /Q network_setup_guide.md

echo.
echo Removing old test files...
del /Q test_threshold_control.py

echo.
echo Cleaning up cache directories...
rmdir /S /Q __pycache__
rmdir /S /Q .pytest_cache
rmdir /S /Q .idea

echo.
echo Cleaning up old results (keeping latest 3 files)...
cd results
for /f "tokens=*" %%i in ('dir /b /o-d federated_results_*.html ^| findstr /v "sample_results"') do (
    set /a count+=1
    if !count! gtr 3 del "%%i"
)
for /f "tokens=*" %%i in ('dir /b /o-d federated_results_*.csv ^| findstr /v "sample_results"') do (
    set /a count+=1
    if !count! gtr 3 del "%%i"
)
for /f "tokens=*" %%i in ('dir /b /o-d federated_results_*.json ^| findstr /v "sample_results"') do (
    set /a count+=1
    if !count! gtr 3 del "%%i"
)
for /f "tokens=*" %%i in ('dir /b /o-d federated_results_*.txt ^| findstr /v "sample_results"') do (
    set /a count+=1
    if !count! gtr 3 del "%%i"
)
cd ..

echo.
echo ========================================
echo Cleanup completed!
echo ========================================
echo.
echo Essential files remaining:
echo - integrated_system.py (main system)
echo - enhanced_frontend_integration.js (frontend)
echo - index.html (web interface)
echo - All core algorithm files
echo - All federated learning files
echo - Latest results and documentation
echo.
pause 