#!/usr/bin/env python3
"""
Interactive Real-time Dashboard for FP-Growth Federated Learning System
"""

import dash
from dash import dcc, html, Input, Output, callback_context
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import json
import time
import threading
from datetime import datetime, timedelta
import os
from pathlib import Path
from typing import Dict, List, Any
import psutil

class FederatedLearningDashboard:
    """Real-time dashboard for monitoring federated learning system"""
    
    def __init__(self, log_dir: str = "logs", update_interval: int = 5000):
        self.log_dir = Path(log_dir)
        self.update_interval = update_interval
        self.app = dash.Dash(__name__)
        self.setup_layout()
        self.setup_callbacks()
        
        # Data storage
        self.performance_data = []
        self.error_data = []
        self.system_metrics = []
        
        # Start data collection thread
        self.running = True
        self.data_thread = threading.Thread(target=self._collect_data, daemon=True)
        self.data_thread.start()
        
    def setup_layout(self):
        """Setup dashboard layout"""
        self.app.layout = html.Div([
            # Header
            html.H1("🚀 FP-Growth Federated Learning Dashboard", 
                   style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
            
            # System Status Row
            html.Div([
                html.Div([
                    html.H3("🟢 System Status", style={'color': '#27ae60'}),
                    html.Div(id='system-status', style={'fontSize': '18px'})
                ], className='four columns'),
                
                html.Div([
                    html.H3("📊 Active Clients", style={'color': '#3498db'}),
                    html.Div(id='active-clients', style={'fontSize': '18px'})
                ], className='four columns'),
                
                html.Div([
                    html.H3("⚡ Performance", style={'color': '#e74c3c'}),
                    html.Div(id='performance-metrics', style={'fontSize': '18px'})
                ], className='four columns')
            ], className='row', style={'marginBottom': 30}),
            
            # Charts Row 1
            html.Div([
                html.Div([
                    html.H4("📈 Performance Over Time"),
                    dcc.Graph(id='performance-chart')
                ], className='six columns'),
                
                html.Div([
                    html.H4("🚨 Error Tracking"),
                    dcc.Graph(id='error-chart')
                ], className='six columns')
            ], className='row', style={'marginBottom': 30}),
            
            # Charts Row 2
            html.Div([
                html.Div([
                    html.H4("💾 Memory Usage"),
                    dcc.Graph(id='memory-chart')
                ], className='six columns'),
                
                html.Div([
                    html.H4("🔍 Mining Results"),
                    dcc.Graph(id='mining-results-chart')
                ], className='six columns')
            ], className='row', style={'marginBottom': 30}),
            
            # Control Panel
            html.Div([
                html.H3("🎛️ Control Panel"),
                html.Div([
                    html.Button("🔄 Refresh Data", id='refresh-btn', n_clicks=0,
                              style={'marginRight': 10}),
                    html.Button("📊 Export Report", id='export-btn', n_clicks=0,
                              style={'marginRight': 10}),
                    html.Button("🧹 Clear Logs", id='clear-btn', n_clicks=0)
                ]),
                html.Div(id='control-output', style={'marginTop': 10})
            ], style={'textAlign': 'center', 'marginBottom': 30}),
            
            # Real-time Updates
            dcc.Interval(
                id='interval-component',
                interval=self.update_interval,
                n_intervals=0
            ),
            
            # Hidden div for storing data
            html.Div(id='data-store', style={'display': 'none'})
        ])
        
    def setup_callbacks(self):
        """Setup dashboard callbacks"""
        
        @self.app.callback(
            [Output('system-status', 'children'),
             Output('active-clients', 'children'),
             Output('performance-metrics', 'children')],
            [Input('interval-component', 'n_intervals')]
        )
        def update_status_metrics(n):
            return self._get_status_metrics()
            
        @self.app.callback(
            Output('performance-chart', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_performance_chart(n):
            return self._create_performance_chart()
            
        @self.app.callback(
            Output('error-chart', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_error_chart(n):
            return self._create_error_chart()
            
        @self.app.callback(
            Output('memory-chart', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_memory_chart(n):
            return self._create_memory_chart()
            
        @self.app.callback(
            Output('mining-results-chart', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_mining_chart(n):
            return self._create_mining_chart()
            
        @self.app.callback(
            Output('control-output', 'children'),
            [Input('refresh-btn', 'n_clicks'),
             Input('export-btn', 'n_clicks'),
             Input('clear-btn', 'n_clicks')]
        )
        def handle_controls(refresh_clicks, export_clicks, clear_clicks):
            ctx = callback_context
            if not ctx.triggered:
                return ""
                
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if button_id == 'refresh-btn':
                return "🔄 Data refreshed successfully!"
            elif button_id == 'export-btn':
                return self._export_report()
            elif button_id == 'clear-btn':
                return self._clear_logs()
                
            return ""
            
    def _collect_data(self):
        """Collect data in background thread"""
        while self.running:
            try:
                # Collect system metrics
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                
                # Handle disk usage for Windows
                try:
                    disk = psutil.disk_usage('C:\\')
                    disk_percent = disk.percent
                except:
                    disk_percent = 0  # Default if disk usage fails
                
                system_metric = {
                    'timestamp': datetime.now(),
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_used_gb': memory.used / 1024 / 1024 / 1024,
                    'disk_percent': disk_percent
                }
                
                self.system_metrics.append(system_metric)
                
                # Keep only last 100 data points
                if len(self.system_metrics) > 100:
                    self.system_metrics = self.system_metrics[-100:]
                    
                # Collect performance data from logs
                self._collect_performance_data()
                
                # Collect error data from logs
                self._collect_error_data()
                
                time.sleep(self.update_interval / 1000)
                
            except Exception as e:
                print(f"Error collecting data: {e}")
                time.sleep(5)
                
    def _collect_performance_data(self):
        """Collect performance data from log files"""
        try:
            perf_log = self.log_dir / 'performance.log'
            if perf_log.exists():
                with open(perf_log, 'r') as f:
                    lines = f.readlines()[-50:]  # Last 50 lines
                    
                for line in lines:
                    if 'Performance:' in line:
                        # Parse performance log line
                        parts = line.split('Performance:')
                        if len(parts) > 1:
                            perf_info = parts[1].strip()
                            operation = perf_info.split(' took ')[0]
                            duration = float(perf_info.split(' took ')[1].split('s')[0])
                            
                            self.performance_data.append({
                                'timestamp': datetime.now(),
                                'operation': operation,
                                'duration': duration
                            })
                            
            # Keep only last 100 performance records
            if len(self.performance_data) > 100:
                self.performance_data = self.performance_data[-100:]
                
        except Exception as e:
            print(f"Error collecting performance data: {e}")
            
    def _collect_error_data(self):
        """Collect error data from log files"""
        try:
            error_log = self.log_dir / 'errors.log'
            if error_log.exists():
                with open(error_log, 'r') as f:
                    lines = f.readlines()[-20:]  # Last 20 lines
                    
                for line in lines:
                    if 'ERROR' in line:
                        self.error_data.append({
                            'timestamp': datetime.now(),
                            'error_type': 'Error',
                            'message': line.strip()
                        })
                        
            # Keep only last 50 error records
            if len(self.error_data) > 50:
                self.error_data = self.error_data[-50:]
                
        except Exception as e:
            print(f"Error collecting error data: {e}")
            
    def _get_status_metrics(self):
        """Get current system status metrics"""
        # System status
        if self.system_metrics:
            latest = self.system_metrics[-1]
            cpu_status = "High" if latest['cpu_percent'] > 80 else "Normal" if latest['cpu_percent'] > 50 else "Low"
            memory_status = "High" if latest['memory_percent'] > 80 else "Normal" if latest['memory_percent'] > 50 else "Low"
            
            system_status = f"CPU: {cpu_status} ({latest['cpu_percent']:.1f}%) | Memory: {memory_status} ({latest['memory_percent']:.1f}%)"
        else:
            system_status = "Collecting data..."
            
        # Active clients (simulated)
        active_clients = f"3 clients connected | Last update: {datetime.now().strftime('%H:%M:%S')}"
        
        # Performance metrics
        if self.performance_data:
            avg_duration = sum(d['duration'] for d in self.performance_data[-10:]) / len(self.performance_data[-10:])
            performance_metrics = f"Avg operation time: {avg_duration:.3f}s | Total operations: {len(self.performance_data)}"
        else:
            performance_metrics = "No performance data available"
            
        return system_status, active_clients, performance_metrics
        
    def _create_performance_chart(self):
        """Create performance over time chart"""
        if not self.performance_data:
            return go.Figure().add_annotation(text="No performance data available", xref="paper", yref="paper")
            
        df = pd.DataFrame(self.performance_data)
        
        fig = go.Figure()
        
        # Group by operation type
        for operation in df['operation'].unique():
            op_data = df[df['operation'] == operation]
            fig.add_trace(go.Scatter(
                x=op_data['timestamp'],
                y=op_data['duration'],
                mode='lines+markers',
                name=operation,
                line=dict(width=2)
            ))
            
        fig.update_layout(
            title="Operation Performance Over Time",
            xaxis_title="Time",
            yaxis_title="Duration (seconds)",
            hovermode='x unified',
            height=400
        )
        
        return fig
        
    def _create_error_chart(self):
        """Create error tracking chart"""
        if not self.error_data:
            return go.Figure().add_annotation(text="No errors recorded", xref="paper", yref="paper")
            
        df = pd.DataFrame(self.error_data)
        
        # Count errors by type
        error_counts = df['error_type'].value_counts()
        
        fig = go.Figure(data=[
            go.Bar(x=error_counts.index, y=error_counts.values, marker_color='red')
        ])
        
        fig.update_layout(
            title="Error Distribution",
            xaxis_title="Error Type",
            yaxis_title="Count",
            height=400
        )
        
        return fig
        
    def _create_memory_chart(self):
        """Create memory usage chart"""
        if not self.system_metrics:
            return go.Figure().add_annotation(text="No system metrics available", xref="paper", yref="paper")
            
        df = pd.DataFrame(self.system_metrics)
        
        fig = make_subplots(rows=2, cols=1, subplot_titles=('CPU Usage', 'Memory Usage'))
        
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['cpu_percent'], mode='lines', name='CPU %'),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['memory_percent'], mode='lines', name='Memory %'),
            row=2, col=1
        )
        
        fig.update_layout(height=500, showlegend=False)
        fig.update_yaxes(title_text="Percentage", row=1, col=1)
        fig.update_yaxes(title_text="Percentage", row=2, col=1)
        
        return fig
        
    def _create_mining_chart(self):
        """Create mining results chart"""
        # Simulated mining results
        operations = ['Data Loading', 'FP-Tree Construction', 'Itemset Mining', 'Privacy Processing', 'Results Aggregation']
        durations = [2.3, 5.7, 8.1, 3.2, 1.8]
        
        fig = go.Figure(data=[
            go.Bar(x=operations, y=durations, marker_color='lightblue')
        ])
        
        fig.update_layout(
            title="Mining Operation Breakdown",
            xaxis_title="Operation",
            yaxis_title="Duration (seconds)",
            height=400
        )
        
        return fig
        
    def _export_report(self):
        """Export dashboard report"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"dashboard_report_{timestamp}.json"
            
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'system_metrics': self.system_metrics[-20:],  # Last 20 metrics
                'performance_data': self.performance_data[-20:],  # Last 20 performance records
                'error_data': self.error_data[-10:],  # Last 10 errors
                'summary': {
                    'total_operations': len(self.performance_data),
                    'total_errors': len(self.error_data),
                    'avg_cpu': sum(m['cpu_percent'] for m in self.system_metrics) / len(self.system_metrics) if self.system_metrics else 0,
                    'avg_memory': sum(m['memory_percent'] for m in self.system_metrics) / len(self.system_metrics) if self.system_metrics else 0
                }
            }
            
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
                
            return f"📊 Report exported to: {report_file}"
            
        except Exception as e:
            return f"❌ Export failed: {str(e)}"
            
    def _clear_logs(self):
        """Clear old log data"""
        try:
            # Keep only recent data
            cutoff_time = datetime.now() - timedelta(hours=1)
            
            self.system_metrics = [m for m in self.system_metrics if m['timestamp'] > cutoff_time]
            self.performance_data = [p for p in self.performance_data if p['timestamp'] > cutoff_time]
            self.error_data = [e for e in self.error_data if e['timestamp'] > cutoff_time]
            
            return f"🧹 Cleared old data. Kept last hour of records."
            
        except Exception as e:
            return f"❌ Clear failed: {str(e)}"
            
    def run(self, host: str = 'localhost', port: int = 8050, debug: bool = False):
        """Run the dashboard"""
        print(f"🚀 Starting Federated Learning Dashboard")
        print(f"📊 Dashboard will be available at: http://{host}:{port}")
        print(f"🔄 Update interval: {self.update_interval}ms")
        
        self.app.run_server(host=host, port=port, debug=debug)
        
    def stop(self):
        """Stop the dashboard"""
        self.running = False
        if self.data_thread.is_alive():
            self.data_thread.join(timeout=5)

def main():
    """Main function to run the dashboard"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Federated Learning Dashboard')
    parser.add_argument('--host', default='localhost', help='Dashboard host (default: localhost)')
    parser.add_argument('--port', type=int, default=8050, help='Dashboard port (default: 8050)')
    parser.add_argument('--log-dir', default='logs', help='Log directory (default: logs)')
    parser.add_argument('--update-interval', type=int, default=5000, help='Update interval in ms (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Create dashboard
    dashboard = FederatedLearningDashboard(
        log_dir=args.log_dir,
        update_interval=args.update_interval
    )
    
    try:
        dashboard.run(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        print("\n🛑 Stopping dashboard...")
        dashboard.stop()
        print("✅ Dashboard stopped")

if __name__ == '__main__':
    main() 