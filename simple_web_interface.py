#!/usr/bin/env python3
"""
Simple Web Interface for FP-Growth Federated Learning System
Lightweight Flask-based interface for basic control and monitoring
"""

from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import json
import time
import threading
import subprocess
import os
import sys
from datetime import datetime
import psutil

app = Flask(__name__)

# Global state
system_status = {
    'server_running': False,
    'clients_connected': 0,
    'mining_active': False,
    'last_update': datetime.now()
}

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FP-Growth Federated Learning - Simple Interface</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #2c3e50, #34495e);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }
        .content {
            padding: 30px;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .status-card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            border-left: 4px solid #3498db;
            transition: transform 0.3s ease;
        }
        .status-card:hover {
            transform: translateY(-5px);
        }
        .status-card h3 {
            margin: 0 0 10px 0;
            color: #2c3e50;
        }
        .status-card .value {
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
        }
        .status-card .label {
            color: #7f8c8d;
            font-size: 0.9em;
            margin-top: 5px;
        }
        .controls {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        .btn {
            padding: 15px 25px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }
        .btn-primary {
            background: #3498db;
            color: white;
        }
        .btn-success {
            background: #27ae60;
            color: white;
        }
        .btn-danger {
            background: #e74c3c;
            color: white;
        }
        .btn-warning {
            background: #f39c12;
            color: white;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .info-section {
            background: #ecf0f1;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .info-section h3 {
            margin: 0 0 15px 0;
            color: #2c3e50;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .info-item {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }
        .info-item strong {
            color: #2c3e50;
        }
        .log-section {
            background: #2c3e50;
            color: #ecf0f1;
            border-radius: 10px;
            padding: 20px;
            font-family: 'Courier New', monospace;
            max-height: 300px;
            overflow-y: auto;
        }
        .log-section h3 {
            margin: 0 0 15px 0;
            color: #3498db;
        }
        .log-entry {
            margin: 5px 0;
            padding: 5px;
            border-radius: 4px;
            background: rgba(255,255,255,0.1);
        }
        .refresh-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            font-size: 1.5em;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }
        .refresh-btn:hover {
            transform: rotate(180deg);
            background: #2980b9;
        }
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2em;
            }
            .content {
                padding: 20px;
            }
            .status-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 FP-Growth Federated Learning</h1>
            <p>Simple Web Interface for System Control and Monitoring</p>
        </div>
        
        <div class="content">
            <!-- Status Cards -->
            <div class="status-grid">
                <div class="status-card">
                    <h3>Server Status</h3>
                    <div class="value" id="server-status">{{ "🟢 Running" if system_status.server_running else "🔴 Stopped" }}</div>
                    <div class="label">Federated Server</div>
                </div>
                
                <div class="status-card">
                    <h3>Connected Clients</h3>
                    <div class="value" id="clients-count">{{ system_status.clients_connected }}</div>
                    <div class="label">Active Connections</div>
                </div>
                
                <div class="status-card">
                    <h3>Mining Status</h3>
                    <div class="value" id="mining-status">{{ "🟢 Active" if system_status.mining_active else "⚪ Idle" }}</div>
                    <div class="label">Current Operation</div>
                </div>
                
                <div class="status-card">
                    <h3>System Health</h3>
                    <div class="value" id="system-health">🟢 Good</div>
                    <div class="label">Overall Status</div>
                </div>
            </div>
            
            <!-- Control Buttons -->
            <div class="controls">
                <a href="/start_server" class="btn btn-primary">🚀 Start Server</a>
                <a href="/stop_server" class="btn btn-danger">🛑 Stop Server</a>
                <a href="/start_mining" class="btn btn-success">⛏️ Start Mining</a>
                <a href="/stop_mining" class="btn btn-warning">⏹️ Stop Mining</a>
                <a href="/run_test" class="btn btn-primary">🧪 Run Test</a>
                <a href="/view_results" class="btn btn-success">📊 View Results</a>
            </div>
            
            <!-- System Information -->
            <div class="info-section">
                <h3>📋 System Information</h3>
                <div class="info-grid">
                    <div class="info-item">
                        <strong>Python Version:</strong><br>
                        {{ python_version }}
                    </div>
                    <div class="info-item">
                        <strong>System Platform:</strong><br>
                        {{ platform }}
                    </div>
                    <div class="info-item">
                        <strong>CPU Usage:</strong><br>
                        {{ cpu_usage }}%
                    </div>
                    <div class="info-item">
                        <strong>Memory Usage:</strong><br>
                        {{ memory_usage }}%
                    </div>
                    <div class="info-item">
                        <strong>Last Update:</strong><br>
                        {{ system_status.last_update.strftime('%H:%M:%S') }}
                    </div>
                    <div class="info-item">
                        <strong>Uptime:</strong><br>
                        {{ uptime }}
                    </div>
                </div>
            </div>
            
            <!-- Quick Actions -->
            <div class="info-section">
                <h3>⚡ Quick Actions</h3>
                <div class="controls">
                    <a href="/quick_mining" class="btn btn-success">⚡ Quick Mining</a>
                    <a href="/benchmark" class="btn btn-primary">📈 Run Benchmark</a>
                    <a href="/generate_dataset" class="btn btn-warning">📊 Generate Dataset</a>
                    <a href="/clean_logs" class="btn btn-danger">🧹 Clean Logs</a>
                </div>
            </div>
            
            <!-- System Logs -->
            <div class="log-section">
                <h3>📝 Recent System Logs</h3>
                <div id="logs">
                    {% for log in recent_logs %}
                    <div class="log-entry">{{ log }}</div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
    
    <button class="refresh-btn" onclick="location.reload()">🔄</button>
    
    <script>
        // Auto-refresh every 5 seconds
        setInterval(function() {
            location.reload();
        }, 5000);
        
        // Add some interactivity
        document.addEventListener('DOMContentLoaded', function() {
            // Add click effects to buttons
            const buttons = document.querySelectorAll('.btn');
            buttons.forEach(button => {
                button.addEventListener('click', function(e) {
                    // Add loading state
                    const originalText = this.innerHTML;
                    this.innerHTML = '⏳ Loading...';
                    this.style.opacity = '0.7';
                    
                    // Reset after 2 seconds
                    setTimeout(() => {
                        this.innerHTML = originalText;
                        this.style.opacity = '1';
                    }, 2000);
                });
            });
        });
    </script>
</body>
</html>
"""

# System logs
system_logs = []

def add_log(message):
    """Add a log message"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    system_logs.append(log_entry)
    if len(system_logs) > 50:  # Keep only last 50 logs
        system_logs.pop(0)

@app.route('/')
def index():
    """Main page"""
    # Get system information
    python_version = sys.version.split()[0]
    platform = sys.platform
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent
    
    # Calculate uptime
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = str(datetime.now() - boot_time).split('.')[0]
    
    return render_template_string(HTML_TEMPLATE, 
                                system_status=system_status,
                                python_version=python_version,
                                platform=platform,
                                cpu_usage=cpu_usage,
                                memory_usage=memory_usage,
                                uptime=uptime,
                                recent_logs=system_logs[-10:])  # Show last 10 logs

@app.route('/start_server')
def start_server():
    """Start the federated server"""
    try:
        add_log("Starting federated server...")
        # This would actually start your server
        system_status['server_running'] = True
        system_status['last_update'] = datetime.now()
        add_log("Federated server started successfully")
        return redirect('/')
    except Exception as e:
        add_log(f"Failed to start server: {str(e)}")
        return redirect('/')

@app.route('/stop_server')
def stop_server():
    """Stop the federated server"""
    try:
        add_log("Stopping federated server...")
        system_status['server_running'] = False
        system_status['clients_connected'] = 0
        system_status['last_update'] = datetime.now()
        add_log("Federated server stopped")
        return redirect('/')
    except Exception as e:
        add_log(f"Failed to stop server: {str(e)}")
        return redirect('/')

@app.route('/start_mining')
def start_mining():
    """Start mining operation"""
    try:
        add_log("Starting HUI mining operation...")
        system_status['mining_active'] = True
        system_status['last_update'] = datetime.now()
        add_log("Mining operation started")
        return redirect('/')
    except Exception as e:
        add_log(f"Failed to start mining: {str(e)}")
        return redirect('/')

@app.route('/stop_mining')
def stop_mining():
    """Stop mining operation"""
    try:
        add_log("Stopping mining operation...")
        system_status['mining_active'] = False
        system_status['last_update'] = datetime.now()
        add_log("Mining operation stopped")
        return redirect('/')
    except Exception as e:
        add_log(f"Failed to stop mining: {str(e)}")
        return redirect('/')

@app.route('/run_test')
def run_test():
    """Run system test"""
    try:
        add_log("Running federated system test...")
        # This would run your test_federated_system.py
        result = subprocess.run([sys.executable, 'test_federated_system.py'], 
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            add_log("System test completed successfully")
        else:
            add_log(f"System test failed: {result.stderr}")
        return redirect('/')
    except Exception as e:
        add_log(f"Failed to run test: {str(e)}")
        return redirect('/')

@app.route('/view_results')
def view_results():
    """View mining results"""
    try:
        add_log("Opening results directory...")
        results_dir = "results"
        if os.path.exists(results_dir):
            # Open results directory
            if sys.platform == "win32":
                os.startfile(results_dir)
            else:
                subprocess.run(["open", results_dir])
            add_log("Results directory opened")
        else:
            add_log("No results directory found")
        return redirect('/')
    except Exception as e:
        add_log(f"Failed to open results: {str(e)}")
        return redirect('/')

@app.route('/quick_mining')
def quick_mining():
    """Run quick mining operation"""
    try:
        add_log("Starting quick mining with website generation...")
        # This would run your run_hui_mining_and_website.py
        result = subprocess.run([sys.executable, 'run_hui_mining_and_website.py'], 
                              capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            add_log("Quick mining completed successfully")
        else:
            add_log(f"Quick mining failed: {result.stderr}")
        return redirect('/')
    except Exception as e:
        add_log(f"Failed to run quick mining: {str(e)}")
        return redirect('/')

@app.route('/benchmark')
def benchmark():
    """Run performance benchmark"""
    try:
        add_log("Starting performance benchmark...")
        # This would run your performance_benchmark.py
        result = subprocess.run([sys.executable, 'performance_benchmark.py'], 
                              capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            add_log("Benchmark completed successfully")
        else:
            add_log(f"Benchmark failed: {result.stderr}")
        return redirect('/')
    except Exception as e:
        add_log(f"Failed to run benchmark: {str(e)}")
        return redirect('/')

@app.route('/generate_dataset')
def generate_dataset():
    """Generate sample dataset"""
    try:
        add_log("Generating sample dataset...")
        # This would run your generate_dataset.py
        result = subprocess.run([sys.executable, 'generate_dataset.py'], 
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            add_log("Dataset generated successfully")
        else:
            add_log(f"Dataset generation failed: {result.stderr}")
        return redirect('/')
    except Exception as e:
        add_log(f"Failed to generate dataset: {str(e)}")
        return redirect('/')

@app.route('/clean_logs')
def clean_logs():
    """Clean system logs"""
    try:
        add_log("Cleaning system logs...")
        global system_logs
        system_logs = []
        system_logs.append("System logs cleaned")
        return redirect('/')
    except Exception as e:
        add_log(f"Failed to clean logs: {str(e)}")
        return redirect('/')

@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    return jsonify({
        'server_running': system_status['server_running'],
        'clients_connected': system_status['clients_connected'],
        'mining_active': system_status['mining_active'],
        'last_update': system_status['last_update'].isoformat(),
        'cpu_usage': psutil.cpu_percent(),
        'memory_usage': psutil.virtual_memory().percent
    })

def update_system_status():
    """Background thread to update system status"""
    while True:
        try:
            # Simulate client connections
            if system_status['server_running']:
                system_status['clients_connected'] = min(3, system_status['clients_connected'] + 1)
            else:
                system_status['clients_connected'] = 0
                
            system_status['last_update'] = datetime.now()
            time.sleep(10)  # Update every 10 seconds
            
        except Exception as e:
            add_log(f"Status update error: {str(e)}")
            time.sleep(30)

def main():
    """Main function"""
    print("🌐 Starting Simple Web Interface for FP-Growth Federated Learning")
    print("📊 Interface will be available at: http://localhost:5000")
    print("🔄 Auto-refresh every 5 seconds")
    
    # Start background status update thread
    status_thread = threading.Thread(target=update_system_status, daemon=True)
    status_thread.start()
    
    # Add initial log
    add_log("Simple web interface started")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    main() 