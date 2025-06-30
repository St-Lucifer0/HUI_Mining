#!/usr/bin/env python3
"""
Enhanced Error Handling and Logging System for FP-Growth Federated Learning
"""

import logging
import traceback
import sys
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from functools import wraps
import json
import threading
from pathlib import Path

class FederatedErrorHandler:
    """Centralized error handling and logging for the federated learning system"""
    
    def __init__(self, log_dir: str = "logs", log_level: str = "INFO"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Configure logging
        self.setup_logging(log_level)
        
        # Error tracking
        self.error_counts = {}
        self.error_history = []
        self.recovery_attempts = {}
        
        # Performance monitoring
        self.operation_times = {}
        self.memory_usage = {}
        
    def setup_logging(self, log_level: str):
        """Setup comprehensive logging configuration"""
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Main logger
        self.logger = logging.getLogger('federated_system')
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # File handlers
        # Detailed logs
        detailed_handler = logging.FileHandler(self.log_dir / 'detailed.log')
        detailed_handler.setLevel(logging.DEBUG)
        detailed_handler.setFormatter(detailed_formatter)
        
        # Error logs
        error_handler = logging.FileHandler(self.log_dir / 'errors.log')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        
        # Performance logs
        perf_handler = logging.FileHandler(self.log_dir / 'performance.log')
        perf_handler.setLevel(logging.INFO)
        perf_handler.setFormatter(simple_formatter)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        
        # Add handlers
        self.logger.addHandler(detailed_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(perf_handler)
        self.logger.addHandler(console_handler)
        
    def log_operation(self, operation: str, details: Dict[str, Any] = None):
        """Log operation details"""
        log_data = {
            'operation': operation,
            'timestamp': datetime.now().isoformat(),
            'thread_id': threading.get_ident(),
            'details': details or {}
        }
        
        self.logger.info(f"Operation: {operation}", extra={'log_data': log_data})
        
    def log_error(self, error: Exception, context: str = "", recovery_action: str = ""):
        """Log error with context and recovery information"""
        error_type = type(error).__name__
        
        # Track error counts
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Create error record
        error_record = {
            'timestamp': datetime.now().isoformat(),
            'error_type': error_type,
            'error_message': str(error),
            'context': context,
            'recovery_action': recovery_action,
            'traceback': traceback.format_exc(),
            'thread_id': threading.get_ident()
        }
        
        self.error_history.append(error_record)
        
        # Log error
        self.logger.error(
            f"Error in {context}: {error_type} - {str(error)}",
            extra={'error_record': error_record}
        )
        
        # Log recovery action if provided
        if recovery_action:
            self.logger.info(f"Recovery action: {recovery_action}")
            
    def log_performance(self, operation: str, duration: float, memory_usage: float = None):
        """Log performance metrics"""
        if operation not in self.operation_times:
            self.operation_times[operation] = []
            
        self.operation_times[operation].append(duration)
        
        if memory_usage:
            if operation not in self.memory_usage:
                self.memory_usage[operation] = []
            self.memory_usage[operation].append(memory_usage)
            
        self.logger.info(
            f"Performance: {operation} took {duration:.3f}s",
            extra={'performance_data': {
                'operation': operation,
                'duration': duration,
                'memory_usage': memory_usage
            }}
        )
        
    def error_handler(self, context: str = "", recovery_action: str = ""):
        """Decorator for automatic error handling"""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    self.log_error(e, context, recovery_action)
                    raise
            return wrapper
        return decorator
        
    def performance_monitor(self, operation: str):
        """Decorator for performance monitoring"""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                import time
                import psutil
                
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss / 1024 / 1024
                
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    end_memory = psutil.Process().memory_info().rss / 1024 / 1024
                    memory_used = end_memory - start_memory
                    
                    self.log_performance(operation, duration, memory_used)
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    self.log_performance(operation, duration)
                    raise
            return wrapper
        return decorator
        
    def retry_on_error(self, max_attempts: int = 3, delay: float = 1.0, 
                      backoff_factor: float = 2.0, exceptions: tuple = (Exception,)):
        """Decorator for retrying operations on error"""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                import time
                
                last_exception = None
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        if attempt < max_attempts - 1:
                            wait_time = delay * (backoff_factor ** attempt)
                            self.logger.warning(
                                f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. "
                                f"Retrying in {wait_time:.2f}s..."
                            )
                            time.sleep(wait_time)
                        else:
                            self.logger.error(
                                f"All {max_attempts} attempts failed for {func.__name__}: {str(e)}"
                            )
                            
                raise last_exception
            return wrapper
        return decorator
        
    def generate_error_report(self) -> Dict[str, Any]:
        """Generate comprehensive error report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'error_summary': {
                'total_errors': len(self.error_history),
                'error_types': self.error_counts,
                'most_common_error': max(self.error_counts.items(), key=lambda x: x[1]) if self.error_counts else None
            },
            'performance_summary': {
                'operations_monitored': len(self.operation_times),
                'avg_durations': {
                    op: sum(times) / len(times) 
                    for op, times in self.operation_times.items()
                },
                'max_durations': {
                    op: max(times) 
                    for op, times in self.operation_times.items()
                }
            },
            'recent_errors': self.error_history[-10:] if self.error_history else [],
            'system_info': {
                'python_version': sys.version,
                'platform': sys.platform,
                'log_directory': str(self.log_dir)
            }
        }
        
        return report
        
    def save_error_report(self, filename: str = None):
        """Save error report to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"error_report_{timestamp}.json"
            
        report = self.generate_error_report()
        report_path = self.log_dir / filename
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        self.logger.info(f"Error report saved to: {report_path}")
        return report_path
        
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """Clean up old log files"""
        import time
        cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
        
        cleaned_count = 0
        for log_file in self.log_dir.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_time:
                log_file.unlink()
                cleaned_count += 1
                
        self.logger.info(f"Cleaned up {cleaned_count} old log files")
        
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status"""
        recent_errors = [e for e in self.error_history 
                        if (datetime.now() - datetime.fromisoformat(e['timestamp'])).seconds < 3600]
        
        return {
            'status': 'healthy' if len(recent_errors) == 0 else 'degraded' if len(recent_errors) < 5 else 'unhealthy',
            'recent_errors_count': len(recent_errors),
            'total_errors_today': len([e for e in self.error_history 
                                     if (datetime.now() - datetime.fromisoformat(e['timestamp'])).days == 0]),
            'error_rate': len(recent_errors) / 60 if recent_errors else 0,  # errors per minute
            'last_error': self.error_history[-1] if self.error_history else None
        }

# Global error handler instance
error_handler = FederatedErrorHandler()

# Convenience functions
def log_operation(operation: str, details: Dict[str, Any] = None):
    """Log an operation"""
    error_handler.log_operation(operation, details)

def log_error(error: Exception, context: str = "", recovery_action: str = ""):
    """Log an error"""
    error_handler.log_error(error, context, recovery_action)

def handle_errors(context: str = "", recovery_action: str = ""):
    """Error handling decorator"""
    return error_handler.error_handler(context, recovery_action)

def monitor_performance(operation: str):
    """Performance monitoring decorator"""
    return error_handler.performance_monitor(operation)

def retry_operation(max_attempts: int = 3, delay: float = 1.0, 
                   backoff_factor: float = 2.0, exceptions: tuple = (Exception,)):
    """Retry operation decorator"""
    return error_handler.retry_on_error(max_attempts, delay, backoff_factor, exceptions)

# Example usage
if __name__ == "__main__":
    # Example of using the error handling system
    @handle_errors("data_processing", "Retrying with smaller batch size")
    @monitor_performance("data_processing")
    @retry_operation(max_attempts=3, delay=1.0)
    def example_function():
        """Example function demonstrating error handling"""
        import random
        
        # Simulate some work
        time.sleep(0.1)
        
        # Simulate occasional errors
        if random.random() < 0.3:
            raise ValueError("Simulated error for testing")
            
        return "Success"
    
    # Test the error handling
    for i in range(5):
        try:
            result = example_function()
            print(f"Attempt {i+1}: {result}")
        except Exception as e:
            print(f"Attempt {i+1}: Failed - {e}")
    
    # Generate and save error report
    error_handler.save_error_report()
    
    # Print health status
    health = error_handler.get_health_status()
    print(f"\nSystem Health: {health['status']}")
    print(f"Recent Errors: {health['recent_errors_count']}")
    print(f"Error Rate: {health['error_rate']:.2f} errors/minute") 