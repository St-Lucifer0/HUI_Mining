# Performance Monitoring for Presentations

This guide shows you how to check memory usage and runtime speed for your HUI mining system during presentations.

## Quick Start

### Option 1: Easy Batch File (Recommended for Presentations)
```bash
# Double-click or run:
run_benchmark.bat
```

This opens a menu where you can choose:
1. **Quick Performance Check** - Fast system overview
2. **System Resources Check** - Detailed hardware info
3. **Data Loading Benchmark** - Test data loading speed
4. **Mining Phases Benchmark** - Test each mining phase
5. **Privacy Mining Benchmark** - Test privacy features
6. **Full Benchmark Suite** - Complete performance test
7. **Run HUI Mining with Monitoring** - Full system with live monitoring

### Option 2: Command Line
```bash
# Quick system check
python presentation_benchmark.py quick

# Check system resources
python presentation_benchmark.py system

# Benchmark data loading
python presentation_benchmark.py loading

# Benchmark mining phases
python presentation_benchmark.py phases

# Benchmark privacy mining
python presentation_benchmark.py privacy

# Run full benchmark suite
python presentation_benchmark.py full
```

## What You'll See

### Live Monitoring Output
```
📊 Starting Performance Monitor: HUI Mining and Website Generation
============================================================
⏰ Start Time: 14:30:25
💾 Initial Memory: 45.23 MB
============================================================
⏱️  1.0s | 💾 46.1MB (+0.9MB) | 🖥️  15.2% CPU
⏱️  2.0s | 💾 47.3MB (+2.1MB) | 🖥️  18.7% CPU
⏱️  3.0s | 💾 48.5MB (+3.3MB) | 🖥️  12.4% CPU
```

### Performance Summary
```
============================================================
📊 PERFORMANCE SUMMARY
============================================================
🎯 Operation: HUI Mining and Website Generation
⏱️  Total Time: 2m 15.3s
💾 Memory Usage: 15.67 MB
📈 Peak Memory: 52.34 MB
🖥️  Average CPU: 18.2%
📊 Average Memory: 48.12 MB
============================================================
```

## Key Metrics Explained

### Memory Usage
- **Initial Memory**: Memory used when starting
- **Memory Usage**: Total additional memory consumed
- **Peak Memory**: Highest memory usage during execution
- **Average Memory**: Average memory usage over time

### Runtime Speed
- **Total Time**: Complete execution time
- **Average CPU**: CPU utilization percentage
- **Phase Breakdown**: Time for each mining phase

### System Resources
- **CPU Cores**: Number of available CPU cores
- **Total Memory**: Available system memory
- **Disk Space**: Available storage space

## Presentation Tips

### 1. Start with System Check
```bash
python presentation_benchmark.py system
```
Shows your hardware capabilities to the audience.

### 2. Quick Performance Overview
```bash
python presentation_benchmark.py quick
```
Fast check showing current system status.

### 3. Live Mining Demonstration
```bash
python run_hui_mining_and_website.py
```
Shows real-time performance during actual mining.

### 4. Phase-by-Phase Analysis
```bash
python presentation_benchmark.py phases
```
Demonstrates performance of each mining step.

## Output Files

All performance reports are saved in the `results/` directory:
- `hui_mining_performance.json` - Main mining performance
- `full_benchmark_YYYYMMDD_HHMMSS.json` - Complete benchmark results
- `performance_report_YYYYMMDD_HHMMSS.json` - Individual test results

## Customization

### Modify Monitoring Frequency
Edit `performance_monitor.py`:
```python
# Change update interval (default: 1 second)
time.sleep(1)  # Change to 0.5 for more frequent updates
```

### Add Custom Metrics
In your main script:
```python
monitor.end_monitoring({
    'custom_metric': your_value,
    'another_metric': another_value
})
```

### Disable Live Monitoring
```python
monitor = PerformanceMonitor(enable_live_monitoring=False)
```

## Troubleshooting

### High Memory Usage
- Check for memory leaks in data processing
- Consider reducing dataset size for demos
- Monitor memory during long-running operations

### Slow Performance
- Check CPU usage during execution
- Verify dataset size and complexity
- Consider adjusting mining parameters

### Monitoring Errors
- Ensure `psutil` is installed: `pip install psutil`
- Check file permissions for output directory
- Verify Python environment compatibility

## Example Presentation Flow

1. **Introduction** (30 seconds)
   ```bash
   python presentation_benchmark.py system
   ```

2. **Data Overview** (1 minute)
   ```bash
   python presentation_benchmark.py loading
   ```

3. **Live Mining Demo** (3-5 minutes)
   ```bash
   python run_hui_mining_and_website.py
   ```

4. **Performance Analysis** (2 minutes)
   - Show saved performance reports
   - Discuss memory and CPU usage
   - Compare different parameters

5. **Q&A with Live Testing** (as needed)
   ```bash
   python presentation_benchmark.py quick
   ```

This setup gives you comprehensive performance monitoring perfect for academic presentations and demonstrations! 