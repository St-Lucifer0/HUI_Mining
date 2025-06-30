#!/usr/bin/env python3
"""
Real-time Performance Monitor for HUI Mining System
Perfect for presentations and demonstrations
"""

import time
import psutil
import os
import threading
from datetime import datetime
from typing import Dict, List, Optional
import json

class PerformanceMonitor:
    """Real-time performance monitoring for presentations"""
    
    def __init__(self, enable_live_monitoring: bool = True):
        self.start_time = None
        self.start_memory = None
        self.monitoring_active = False
        self.live_monitoring = enable_live_monitoring
        self.monitor_thread = None
        self.peak_memory = 0
        self.memory_history = []
        self.cpu_history = []
        self.timestamps = []
        
    def start_monitoring(self, operation_name: str = "HUI Mining"):
        """Start performance monitoring"""
        self.operation_name = operation_name
        self.start_time = time.time()
        self.start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        self.peak_memory = self.start_memory
        self.monitoring_active = True
        
        print(f"\n📊 Starting Performance Monitor: {operation_name}")
        print("=" * 60)
        print(f"⏰ Start Time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"💾 Initial Memory: {self.start_memory:.2f} MB")
        print("=" * 60)
        
        if self.live_monitoring:
            self._start_live_monitoring()
            
    def _start_live_monitoring(self):
        """Start live monitoring in background thread"""
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                current_cpu = psutil.cpu_percent(interval=1)
                current_time = time.time()
                
                self.memory_history.append(current_memory)
                self.cpu_history.append(current_cpu)
                self.timestamps.append(current_time)
                
                self.peak_memory = max(self.peak_memory, current_memory)
                
                # Print live stats every 5 seconds
                if len(self.timestamps) % 5 == 0:
                    elapsed = current_time - self.start_time
                    memory_diff = current_memory - self.start_memory
                    print(f"⏱️  {elapsed:.1f}s | 💾 {current_memory:.1f}MB (+{memory_diff:+.1f}MB) | 🖥️  {current_cpu:.1f}% CPU")
                    
                time.sleep(1)
            except Exception as e:
                print(f"⚠️ Monitoring error: {e}")
                break
                
    def end_monitoring(self, additional_metrics: Dict = None) -> Dict:
        """End monitoring and return performance summary"""
        self.monitoring_active = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
            
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        total_duration = end_time - self.start_time
        total_memory_used = end_memory - self.start_memory
        avg_cpu = sum(self.cpu_history) / len(self.cpu_history) if self.cpu_history else 0
        avg_memory = sum(self.memory_history) / len(self.memory_history) if self.memory_history else 0
        
        results = {
            'operation_name': self.operation_name,
            'total_duration_seconds': total_duration,
            'total_duration_formatted': self._format_duration(total_duration),
            'memory_usage_mb': total_memory_used,
            'peak_memory_mb': self.peak_memory,
            'final_memory_mb': end_memory,
            'average_cpu_percent': avg_cpu,
            'average_memory_mb': avg_memory,
            'start_time': datetime.fromtimestamp(self.start_time).isoformat(),
            'end_time': datetime.fromtimestamp(end_time).isoformat(),
            'memory_history': self.memory_history,
            'cpu_history': self.cpu_history,
            'timestamps': self.timestamps,
            **additional_metrics or {}
        }
        
        self._print_summary(results)
        return results
        
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format"""
        if seconds < 60:
            return f"{seconds:.2f} seconds"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = seconds % 60
            return f"{minutes}m {secs:.1f}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = seconds % 60
            return f"{hours}h {minutes}m {secs:.1f}s"
            
    def _print_summary(self, results: Dict):
        """Print performance summary"""
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE SUMMARY")
        print("=" * 60)
        print(f"🎯 Operation: {results['operation_name']}")
        print(f"⏱️  Total Time: {results['total_duration_formatted']}")
        print(f"💾 Memory Usage: {results['memory_usage_mb']:.2f} MB")
        print(f"📈 Peak Memory: {results['peak_memory_mb']:.2f} MB")
        print(f"🖥️  Average CPU: {results['average_cpu_percent']:.1f}%")
        print(f"📊 Average Memory: {results['average_memory_mb']:.2f} MB")
        print("=" * 60)
        
    def save_report(self, results: Dict, filename: str = None) -> str:
        """Save performance report to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_report_{timestamp}.json"
            
        # Create results directory if it doesn't exist
        os.makedirs("results", exist_ok=True)
        filepath = os.path.join("results", filename)
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
            
        print(f"📄 Performance report saved: {filepath}")
        return filepath

# Convenience functions for easy integration
def monitor_operation(operation_name: str = "Operation", enable_live: bool = True):
    """Decorator to monitor function performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            monitor = PerformanceMonitor(enable_live_monitoring=enable_live)
            monitor.start_monitoring(operation_name)
            
            try:
                result = func(*args, **kwargs)
                additional_metrics = {'success': True}
                if hasattr(result, '__len__'):
                    additional_metrics['result_count'] = len(result)
                monitor.end_monitoring(additional_metrics)
                return result
            except Exception as e:
                monitor.end_monitoring({'success': False, 'error': str(e)})
                raise
        return wrapper
    return decorator

def quick_benchmark(func, *args, iterations: int = 3, **kwargs) -> Dict:
    """Quick benchmark of a function"""
    monitor = PerformanceMonitor(enable_live_monitoring=False)
    results = []
    
    print(f"🏃 Quick Benchmark: {func.__name__} ({iterations} iterations)")
    print("=" * 50)
    
    for i in range(iterations):
        print(f"🔄 Iteration {i+1}/{iterations}...")
        monitor.start_monitoring(f"{func.__name__}_iter_{i+1}")
        
        try:
            result = func(*args, **kwargs)
            iteration_result = monitor.end_monitoring({
                'iteration': i+1,
                'success': True,
                'result_count': len(result) if hasattr(result, '__len__') else 1
            })
            results.append(iteration_result)
        except Exception as e:
            monitor.end_monitoring({'iteration': i+1, 'success': False, 'error': str(e)})
            print(f"❌ Iteration {i+1} failed: {e}")
    
    # Calculate averages
    if results:
        avg_duration = sum(r['total_duration_seconds'] for r in results) / len(results)
        avg_memory = sum(r['memory_usage_mb'] for r in results) / len(results)
        avg_cpu = sum(r['average_cpu_percent'] for r in results) / len(results)
        
        summary = {
            'function_name': func.__name__,
            'iterations': iterations,
            'average_duration_seconds': avg_duration,
            'average_memory_mb': avg_memory,
            'average_cpu_percent': avg_cpu,
            'min_duration': min(r['total_duration_seconds'] for r in results),
            'max_duration': max(r['total_duration_seconds'] for r in results),
            'iterations_results': results
        }
        
        print(f"\n📊 BENCHMARK SUMMARY")
        print(f"⏱️  Average Time: {avg_duration:.2f}s")
        print(f"💾 Average Memory: {avg_memory:.2f}MB")
        print(f"🖥️  Average CPU: {avg_cpu:.1f}%")
        print(f"📈 Min/Max Time: {summary['min_duration']:.2f}s / {summary['max_duration']:.2f}s")
        
        return summary
    
    return {}

if __name__ == "__main__":
    # Example usage
    @monitor_operation("Example Function", enable_live=True)
    def example_function():
        """Example function for testing"""
        import time
        print("🔄 Running example function...")
        time.sleep(3)  # Simulate work
        return [1, 2, 3, 4, 5]
    
    # Test the monitor
    result = example_function()
    print(f"✅ Function completed with result: {result}") 