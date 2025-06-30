@echo off
echo.
echo ========================================
echo    HUI MINING PERFORMANCE BENCHMARKS
echo ========================================
echo.

echo Choose a benchmark option:
echo 1. Quick Performance Check
echo 2. System Resources Check
echo 3. Data Loading Benchmark
echo 4. Mining Phases Benchmark
echo 5. Privacy Mining Benchmark
echo 6. Full Benchmark Suite
echo 7. Run HUI Mining with Monitoring
echo.

set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" (
    echo Running Quick Performance Check...
    python presentation_benchmark.py quick
) else if "%choice%"=="2" (
    echo Checking System Resources...
    python presentation_benchmark.py system
) else if "%choice%"=="3" (
    echo Benchmarking Data Loading...
    python presentation_benchmark.py loading
) else if "%choice%"=="4" (
    echo Benchmarking Mining Phases...
    python presentation_benchmark.py phases
) else if "%choice%"=="5" (
    echo Benchmarking Privacy Mining...
    python presentation_benchmark.py privacy
) else if "%choice%"=="6" (
    echo Running Full Benchmark Suite...
    python presentation_benchmark.py full
) else if "%choice%"=="7" (
    echo Running HUI Mining with Performance Monitoring...
    python run_hui_mining_and_website.py
) else (
    echo Invalid choice. Please run the script again.
)

echo.
echo Press any key to exit...
pause >nul 