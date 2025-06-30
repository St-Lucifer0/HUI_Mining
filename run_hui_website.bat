@echo off
echo.
echo ========================================
echo   HUI Mining with Website Display
echo ========================================
echo.
echo This will:
echo 1. Load your CSV data
echo 2. Run High-Utility Itemset Mining
echo 3. Generate a beautiful website
echo 4. Open results in your browser
echo.
echo Press any key to start...
pause >nul

echo.
echo Starting HUI Mining and Website Generation...
echo.

python run_hui_mining_and_website.py

echo.
echo Process completed!
echo Check the 'results/' folder for all output files.
echo.
pause 