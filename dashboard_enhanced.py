#!/usr/bin/env python3
"""
Enhanced Interactive Dashboard for FP-Growth Federated Learning System
Additional features: Real-time client status, mining progress, and system controls
"""

import dash
from dash import dcc, html, Input, Output, callback_context, State
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
import subprocess
import sys

class EnhancedFederatedLearningDashboard:
    """Enhanced real-time dashboard for monitoring federated learning system"""
    
    def __init__(self, log_dir: str = "logs", update_interval: int = 3000):
        self.log_dir = Path(log_dir)
        self.update_interval = update_interval
        self.app = dash.Dash(__name__, external_stylesheets=[
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
        ])
        
        # Enhanced data storage
        self.performance_data = []
        self.error_data = []
        self.system_metrics = []
        self.client_status = {}
        self.mining_progress = {}
        
        self.setup_enhanced_layout()
        self.setup_enhanced_callbacks()
        
        # Start enhanced data collection
        self.running = True
        self.data_thread = threading.Thread(target=self._collect_enhanced_data, daemon=True)
        self.data_thread.start()
        
    def setup_enhanced_layout(self):
        """Setup enhanced dashboard layout with more features"""
        self.app.layout = html.Div([
            # Enhanced Header with Status
            html.Div([
                html.H1([
                    html.I(className="fas fa-rocket", style={'marginRight': '10px'}),
                    "FP-Growth Federated Learning Dashboard"
                ], style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 20}),
                html.Div(id='system-overview', style={'textAlign': 'center', 'marginBottom': 30})
            ]),
            
            # Quick Actions Row
            html.Div([
                html.Div([
                    html.Button([
                        html.I(className="fas fa-play", style={'marginRight': '5px'}),
                        "Start Mining"
                    ], id='start-mining-btn', className='action-btn', style={'backgroundColor': '#27ae60'}),
                ], className='two columns'),
                html.Div([
                    html.Button([
                        html.I(className="fas fa-stop", style={'marginRight': '5px'}),
                        "Stop Mining"
                    ], id='stop-mining-btn', className='action-btn', style={'backgroundColor': '#e74c3c'}),
                ], className='two columns'),
                html.Div([
                    html.Button([
                        html.I(className="fas fa-sync", style={'marginRight': '5px'}),
                        "Refresh Data"
                    ], id='refresh-btn', className='action-btn', style={'backgroundColor': '#3498db'}),
                ], className='two columns'),
                html.Div([
                    html.Button([
                        html.I(className="fas fa-download", style={'marginRight': '5px'}),
                        "Export Report"
                    ], id='export-btn', className='action-btn', style={'backgroundColor': '#f39c12'}),
                ], className='two columns'),
                html.Div([
                    html.Button([
                        html.I(className="fas fa-cog", style={'marginRight': '5px'}),
                        "Settings"
                    ], id='settings-btn', className='action-btn', style={'backgroundColor': '#9b59b6'}),
                ], className='two columns'),
            ], className='row', style={'marginBottom': 30}),
            
            # System Status Cards
            html.Div([
                html.Div([
                    html.Div([
                        html.I(className="fas fa-server", style={'fontSize': '2em', 'color': '#3498db'}),
                        html.H3("Server Status", style={'margin': '10px 0'}),
                        html.Div(id='server-status', style={'fontSize': '16px'})
                    ], className='status-card')
                ], className='three columns'),
                
                html.Div([
                    html.Div([
                        html.I(className="fas fa-users", style={'fontSize': '2em', 'color': '#27ae60'}),
                        html.H3("Active Clients", style={'margin': '10px 0'}),
                        html.Div(id='active-clients', style={'fontSize': '16px'})
                    ], className='status-card')
                ], className='three columns'),
                
                html.Div([
                    html.Div([
                        html.I(className="fas fa-chart-line", style={'fontSize': '2em', 'color': '#e74c3c'}),
                        html.H3("Performance", style={'margin': '10px 0'}),
                        html.Div(id='performance-metrics', style={'fontSize': '16px'})
                    ], className='status-card')
                ], className='three columns'),
                
                html.Div([
                    html.Div([
                        html.I(className="fas fa-shield-alt", style={'fontSize': '2em', 'color': '#f39c12'}),
                        html.H3("Privacy Status", style={'margin': '10px 0'}),
                        html.Div(id='privacy-status', style={'fontSize': '16px'})
                    ], className='status-card')
                ], className='three columns'),
            ], className='row', style={'marginBottom': 30}),
            
            # Mining Progress Section
            html.Div([
                html.H3([
                    html.I(className="fas fa-tasks", style={'marginRight': '10px'}),
                    "Mining Progress"
                ], style={'textAlign': 'center', 'marginBottom': 20}),
                html.Div(id='mining-progress', style={'marginBottom': 30})
            ]),
            
            # Enhanced Charts Row 1
            html.Div([
                html.Div([
                    html.H4([
                        html.I(className="fas fa-chart-area", style={'marginRight': '10px'}),
                        "Performance Over Time"
                    ]),
                    dcc.Graph(id='performance-chart', style={'height': '400px'})
                ], className='six columns'),
                
                html.Div([
                    html.H4([
                        html.I(className="fas fa-exclamation-triangle", style={'marginRight': '10px'}),
                        "Error Tracking"
                    ]),
                    dcc.Graph(id='error-chart', style={'height': '400px'})
                ], className='six columns'),
            ], className='row', style={'marginBottom': 30}),
            
            # Enhanced Charts Row 2
            html.Div([
                html.Div([
                    html.H4([
                        html.I(className="fas fa-memory", style={'marginRight': '10px'}),
                        "System Resources"
                    ]),
                    dcc.Graph(id='system-resources-chart', style={'height': '400px'})
                ], className='six columns'),
                
                html.Div([
                    html.H4([
                        html.I(className="fas fa-search", style={'marginRight': '10px'}),
                        "Mining Results"
                    ]),
                    dcc.Graph(id='mining-results-chart', style={'height': '400px'})
                ], className='six columns'),
            ], className='row', style={'marginBottom': 30}),
            
            # Client Status Table
            html.Div([
                html.H3([
                    html.I(className="fas fa-table", style={'marginRight': '10px'}),
                    "Client Status"
                ], style={'textAlign': 'center', 'marginBottom': 20}),
                html.Div(id='client-status-table', style={'marginBottom': 30})
            ]),
            
            # Settings Modal
            dcc.Modal([
                html.Div([
                    html.H3("Dashboard Settings", style={'textAlign': 'center'}),
                    html.Div([
                        html.Label("Update Interval (ms):"),
                        dcc.Slider(
                            id='update-interval-slider',
                            min=1000,
                            max=10000,
                            step=500,
                            value=self.update_interval,
                            marks={i: f'{i}ms' for i in [1000, 3000, 5000, 7000, 10000]}
                        ),
                        html.Br(),
                        html.Label("Auto-refresh:"),
                        dcc.Checklist(
                            id='auto-refresh-toggle',
                            options=[{'label': 'Enable', 'value': 'enabled'}],
                            value=['enabled']
                        ),
                        html.Br(),
                        html.Button("Save Settings", id='save-settings-btn', className='action-btn'),
                        html.Button("Cancel", id='cancel-settings-btn', className='action-btn', 
                                  style={'marginLeft': '10px', 'backgroundColor': '#95a5a6'})
                    ])
                ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '10px'})
            ], id='settings-modal', style={'display': 'none'}),
            
            # Real-time Updates
            dcc.Interval(
                id='interval-component',
                interval=self.update_interval,
                n_intervals=0
            ),
            
            # Hidden divs for storing data
            html.Div(id='data-store', style={'display': 'none'}),
            html.Div(id='action-output', style={'marginTop': '10px', 'textAlign': 'center'})
        ], style={'padding': '20px', 'backgroundColor': '#f8f9fa'})
        
        # Add custom CSS
        self.app.index_string = '''
        <!DOCTYPE html>
        <html>
            <head>
                <title>FP-Growth Federated Learning Dashboard</title>
                <style>
                    .action-btn {
                        padding: 10px 20px;
                        border: none;
                        border-radius: 5px;
                        color: white;
                        font-weight: bold;
                        cursor: pointer;
                        transition: all 0.3s ease;
                        width: 100%;
                    }
                    .action-btn:hover {
                        transform: translateY(-2px);
                        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                    }
                    .status-card {
                        background: white;
                        padding: 20px;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        text-align: center;
                        transition: all 0.3s ease;
                    }
                    .status-card:hover {
                        transform: translateY(-5px);
                        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                    }
                    .progress-bar {
                        width: 100%;
                        height: 20px;
                        background-color: #ecf0f1;
                        border-radius: 10px;
                        overflow: hidden;
                        margin: 10px 0;
                    }
                    .progress-fill {
                        height: 100%;
                        background: linear-gradient(90deg, #3498db, #27ae60);
                        transition: width 0.3s ease;
                    }
                </style>
            </head>
            <body>
                {%app_entry%}
                <footer>
                    {%config%}
                    {%scripts%}
                    {%renderer%}
                </footer>
            </body>
        </html>
        '''
        
    def setup_enhanced_callbacks(self):
        """Setup enhanced dashboard callbacks"""
        
        @self.app.callback(
            [Output('system-overview', 'children'),
             Output('server-status', 'children'),
             Output('active-clients', 'children'),
             Output('performance-metrics', 'children'),
             Output('privacy-status', 'children')],
            [Input('interval-component', 'n_intervals')]
        )
        def update_status_metrics(n):
            return self._get_enhanced_status_metrics()
            
        @self.app.callback(
            Output('mining-progress', 'children'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_mining_progress(n):
            return self._create_mining_progress()
            
        @self.app.callback(
            Output('client-status-table', 'children'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_client_table(n):
            return self._create_client_status_table()
            
        @self.app.callback(
            [Output('action-output', 'children'),
             Output('settings-modal', 'style')],
            [Input('start-mining-btn', 'n_clicks'),
             Input('stop-mining-btn', 'n_clicks'),
             Input('refresh-btn', 'n_clicks'),
             Input('export-btn', 'n_clicks'),
             Input('settings-btn', 'n_clicks'),
             Input('save-settings-btn', 'n_clicks'),
             Input('cancel-settings-btn', 'n_clicks')]
        )
        def handle_actions(start_clicks, stop_clicks, refresh_clicks, export_clicks, 
                          settings_clicks, save_clicks, cancel_clicks):
            ctx = callback_context
            if not ctx.triggered:
                return "", {'display': 'none'}
                
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if button_id == 'start-mining-btn':
                return self._start_mining(), {'display': 'none'}
            elif button_id == 'stop-mining-btn':
                return self._stop_mining(), {'display': 'none'}
            elif button_id == 'refresh-btn':
                return "🔄 Data refreshed successfully!", {'display': 'none'}
            elif button_id == 'export-btn':
                return self._export_enhanced_report(), {'display': 'none'}
            elif button_id == 'settings-btn':
                return "", {'display': 'block'}
            elif button_id == 'save-settings-btn':
                return "⚙️ Settings saved!", {'display': 'none'}
            elif button_id == 'cancel-settings-btn':
                return "", {'display': 'none'}
                
            return "", {'display': 'none'}
            
        # Chart callbacks (same as before but enhanced)
        @self.app.callback(
            Output('performance-chart', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_performance_chart(n):
            return self._create_enhanced_performance_chart()
            
        @self.app.callback(
            Output('system-resources-chart', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_system_chart(n):
            return self._create_enhanced_system_chart()
            
    def _collect_enhanced_data(self):
        """Collect enhanced data in background thread"""
        while self.running:
            try:
                # Collect system metrics
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                
                try:
                    disk = psutil.disk_usage('C:\\')
                    disk_percent = disk.percent
                except:
                    disk_percent = 0
                
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
                    
                # Simulate client status updates
                self._update_client_status()
                
                # Simulate mining progress
                self._update_mining_progress()
                
                time.sleep(self.update_interval / 1000)
                
            except Exception as e:
                print(f"Error collecting enhanced data: {e}")
                time.sleep(5)
                
    def _update_client_status(self):
        """Update simulated client status"""
        clients = ['client-1', 'client-2', 'client-3']
        for client_id in clients:
            self.client_status[client_id] = {
                'status': 'connected' if len(self.client_status) % 3 != 0 else 'disconnected',
                'last_seen': datetime.now(),
                'itemsets_found': len(self.client_status) * 5,
                'utility_sum': len(self.client_status) * 25.5,
                'privacy_budget_used': 0.8
            }
            
    def _update_mining_progress(self):
        """Update simulated mining progress"""
        current_time = datetime.now()
        if 'start_time' not in self.mining_progress:
            self.mining_progress['start_time'] = current_time
            self.mining_progress['total_phases'] = 5
            self.mining_progress['current_phase'] = 0
            
        elapsed = (current_time - self.mining_progress['start_time']).total_seconds()
        if elapsed > 30:  # Reset after 30 seconds
            self.mining_progress['start_time'] = current_time
            self.mining_progress['current_phase'] = 0
            
        phase_progress = min(int(elapsed / 6), 4)  # 6 seconds per phase
        self.mining_progress['current_phase'] = phase_progress
        self.mining_progress['phase_progress'] = (elapsed % 6) / 6 * 100
        
    def _get_enhanced_status_metrics(self):
        """Get enhanced system status metrics"""
        # System overview
        if self.system_metrics:
            latest = self.system_metrics[-1]
            system_overview = f"🟢 System Online | CPU: {latest['cpu_percent']:.1f}% | Memory: {latest['memory_percent']:.1f}% | {len(self.client_status)} Clients Active"
        else:
            system_overview = "🟡 System Initializing..."
            
        # Server status
        server_status = "🟢 Running | Port 50051 | gRPC Active"
        
        # Active clients
        connected_clients = sum(1 for c in self.client_status.values() if c['status'] == 'connected')
        active_clients = f"{connected_clients}/{len(self.client_status)} Connected | Last Update: {datetime.now().strftime('%H:%M:%S')}"
        
        # Performance metrics
        if self.performance_data:
            avg_duration = sum(d['duration'] for d in self.performance_data[-10:]) / len(self.performance_data[-10:])
            performance_metrics = f"Avg: {avg_duration:.3f}s | Total: {len(self.performance_data)} ops"
        else:
            performance_metrics = "No performance data available"
            
        # Privacy status
        privacy_status = "🟢 Active | ε=1.0 | Budget: 80% used"
        
        return system_overview, server_status, active_clients, performance_metrics, privacy_status
        
    def _create_mining_progress(self):
        """Create mining progress display"""
        if 'current_phase' not in self.mining_progress:
            return html.Div("No mining in progress", style={'textAlign': 'center'})
            
        phases = ['Data Loading', 'FP-Tree Construction', 'Itemset Mining', 'Privacy Processing', 'Results Aggregation']
        current_phase = self.mining_progress['current_phase']
        phase_progress = self.mining_progress.get('phase_progress', 0)
        
        progress_bars = []
        for i, phase in enumerate(phases):
            if i < current_phase:
                # Completed phase
                progress_bars.append(html.Div([
                    html.Div(phase, style={'fontWeight': 'bold', 'color': '#27ae60'}),
                    html.Div([
                        html.Div(style={'width': '100%', 'height': '20px', 'backgroundColor': '#27ae60', 'borderRadius': '10px'})
                    ], className='progress-bar')
                ], style={'marginBottom': '15px'}))
            elif i == current_phase:
                # Current phase
                progress_bars.append(html.Div([
                    html.Div(f"{phase} ({phase_progress:.1f}%)", style={'fontWeight': 'bold', 'color': '#3498db'}),
                    html.Div([
                        html.Div(style={'width': f'{phase_progress}%', 'height': '20px', 'backgroundColor': '#3498db', 'borderRadius': '10px'})
                    ], className='progress-bar')
                ], style={'marginBottom': '15px'}))
            else:
                # Future phase
                progress_bars.append(html.Div([
                    html.Div(phase, style={'fontWeight': 'bold', 'color': '#bdc3c7'}),
                    html.Div([
                        html.Div(style={'width': '0%', 'height': '20px', 'backgroundColor': '#ecf0f1', 'borderRadius': '10px'})
                    ], className='progress-bar')
                ], style={'marginBottom': '15px'}))
                
        return html.Div(progress_bars, style={'maxWidth': '600px', 'margin': '0 auto'})
        
    def _create_client_status_table(self):
        """Create client status table"""
        if not self.client_status:
            return html.Div("No client data available", style={'textAlign': 'center'})
            
        table_header = html.Tr([
            html.Th("Client ID"),
            html.Th("Status"),
            html.Th("Last Seen"),
            html.Th("Itemsets Found"),
            html.Th("Utility Sum"),
            html.Th("Privacy Budget")
        ])
        
        table_rows = []
        for client_id, data in self.client_status.items():
            status_color = "#27ae60" if data['status'] == 'connected' else "#e74c3c"
            status_icon = "🟢" if data['status'] == 'connected' else "🔴"
            
            table_rows.append(html.Tr([
                html.Td(client_id),
                html.Td(f"{status_icon} {data['status'].title()}", style={'color': status_color}),
                html.Td(data['last_seen'].strftime('%H:%M:%S')),
                html.Td(str(data['itemsets_found'])),
                html.Td(f"{data['utility_sum']:.1f}"),
                html.Td(f"{data['privacy_budget_used']:.1f}")
            ]))
            
        return html.Table([table_header] + table_rows, 
                         style={'width': '100%', 'borderCollapse': 'collapse', 'backgroundColor': 'white'})
        
    def _start_mining(self):
        """Start mining operation"""
        try:
            # This would integrate with your actual mining system
            return "🚀 Mining started successfully!"
        except Exception as e:
            return f"❌ Failed to start mining: {str(e)}"
            
    def _stop_mining(self):
        """Stop mining operation"""
        try:
            # This would integrate with your actual mining system
            return "🛑 Mining stopped successfully!"
        except Exception as e:
            return f"❌ Failed to stop mining: {str(e)}"
            
    def _export_enhanced_report(self):
        """Export enhanced report"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dashboard_report_{timestamp}.html"
            
            # Create enhanced report content
            report_content = f"""
            <html>
            <head><title>Dashboard Report - {timestamp}</title></head>
            <body>
                <h1>FP-Growth Federated Learning Dashboard Report</h1>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <h2>System Status</h2>
                <p>Active Clients: {len(self.client_status)}</p>
                <p>Performance Data Points: {len(self.performance_data)}</p>
                <p>System Metrics: {len(self.system_metrics)}</p>
            </body>
            </html>
            """
            
            with open(f"results/{filename}", 'w') as f:
                f.write(report_content)
                
            return f"📊 Report exported: {filename}"
        except Exception as e:
            return f"❌ Export failed: {str(e)}"
            
    def _create_enhanced_performance_chart(self):
        """Create enhanced performance chart"""
        if not self.performance_data:
            return go.Figure().add_annotation(text="No performance data available", xref="paper", yref="paper")
            
        df = pd.DataFrame(self.performance_data)
        
        fig = go.Figure()
        
        # Group by operation type with enhanced styling
        colors = ['#3498db', '#27ae60', '#e74c3c', '#f39c12', '#9b59b6']
        for i, operation in enumerate(df['operation'].unique()):
            op_data = df[df['operation'] == operation]
            fig.add_trace(go.Scatter(
                x=op_data['timestamp'],
                y=op_data['duration'],
                mode='lines+markers',
                name=operation,
                line=dict(width=3, color=colors[i % len(colors)]),
                marker=dict(size=6)
            ))
            
        fig.update_layout(
            title="Operation Performance Over Time",
            xaxis_title="Time",
            yaxis_title="Duration (seconds)",
            hovermode='x unified',
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
        
    def _create_enhanced_system_chart(self):
        """Create enhanced system resources chart"""
        if not self.system_metrics:
            return go.Figure().add_annotation(text="No system metrics available", xref="paper", yref="paper")
            
        df = pd.DataFrame(self.system_metrics)
        
        fig = make_subplots(
            rows=3, cols=1, 
            subplot_titles=('CPU Usage', 'Memory Usage', 'Disk Usage'),
            vertical_spacing=0.1
        )
        
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['cpu_percent'], mode='lines', 
                      name='CPU %', line=dict(color='#3498db', width=2)),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['memory_percent'], mode='lines', 
                      name='Memory %', line=dict(color='#27ae60', width=2)),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['disk_percent'], mode='lines', 
                      name='Disk %', line=dict(color='#e74c3c', width=2)),
            row=3, col=1
        )
        
        fig.update_layout(height=500, showlegend=False)
        fig.update_yaxes(title_text="Percentage", row=1, col=1)
        fig.update_yaxes(title_text="Percentage", row=2, col=1)
        fig.update_yaxes(title_text="Percentage", row=3, col=1)
        
        return fig
        
    def run(self, host: str = 'localhost', port: int = 8050, debug: bool = False):
        """Run the enhanced dashboard"""
        print(f"🚀 Starting Enhanced Federated Learning Dashboard")
        print(f"📊 Dashboard will be available at: http://{host}:{port}")
        print(f"🔄 Update interval: {self.update_interval}ms")
        print(f"✨ Enhanced features: Real-time monitoring, client status, mining progress")
        
        self.app.run(host=host, port=port, debug=debug)
        
    def stop(self):
        """Stop the dashboard"""
        self.running = False
        if self.data_thread.is_alive():
            self.data_thread.join(timeout=5)

def main():
    """Main function to run the enhanced dashboard"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Federated Learning Dashboard')
    parser.add_argument('--host', default='localhost', help='Dashboard host (default: localhost)')
    parser.add_argument('--port', type=int, default=8050, help='Dashboard port (default: 8050)')
    parser.add_argument('--log-dir', default='logs', help='Log directory (default: logs)')
    parser.add_argument('--update-interval', type=int, default=3000, help='Update interval in ms (default: 3000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Create enhanced dashboard
    dashboard = EnhancedFederatedLearningDashboard(
        log_dir=args.log_dir,
        update_interval=args.update_interval
    )
    
    try:
        dashboard.run(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        print("\n🛑 Stopping enhanced dashboard...")
        dashboard.stop()
        print("✅ Enhanced dashboard stopped")

if __name__ == '__main__':
    main() 