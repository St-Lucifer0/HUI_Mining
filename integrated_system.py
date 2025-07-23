#!/usr/bin/env python3
"""
Integrated FP-Growth Federated Learning System
Combines FP-Growth algorithm, federated learning, and web interface
Supports both server and client modes for multi-laptop deployment
"""

import os
import sys
import json
import time
import threading
import logging
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import webbrowser

# Flask and API imports
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room

# gRPC imports for federated learning
import grpc
from concurrent import futures

# Import existing modules
try:
    from config import get_min_utility_threshold, set_min_utility_threshold, reset_min_utility_threshold
    from data_parser import DataProcessor
    from preprocessor import construct_pruned_item_list
    from fp_tree_builder import construct_huim_fp_tree
    from hui_miner import HUIMiner
    from privacy_wrapper import PrivacyPreservingHUIMining
    from output_formatter import FederatedLearningOutputFormatter
    from performance_monitor import PerformanceMonitor
    from federated_server import FederatedLearningServer, serve as serve_federated
    from federated_client import FederatedLearningClient
    from federated_learning_pb2 import *
    from federated_learning_pb2_grpc import *
    BACKEND_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Some backend modules not available: {e}")
    BACKEND_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('integrated_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IntegratedSystem:
    """
    Main integrated system that combines all components
    """
    
    def __init__(self, mode='server', host='0.0.0.0', api_port=5000, 
                 federated_port=50051, client_id=None, server_address=None):
        self.mode = mode  # 'server' or 'client'
        self.host = host
        self.api_port = api_port
        self.federated_port = federated_port
        self.client_id = client_id
        self.server_address = server_address
        
        # Initialize components
        self.flask_app = None
        self.socketio = None
        self.federated_server = None
        self.federated_client = None
        self.api_state = None
        
        # Threading
        self.server_thread = None
        self.federated_thread = None
        self.client_thread = None
        self.running = False
        
        # Configuration
        self.config = self._load_config()
        
        logger.info(f"Integrated System initialized in {mode} mode")
    
    def _load_config(self) -> Dict:
        """Load system configuration"""
        config_path = Path('integrated_config.json')
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Default configuration
            default_config = {
                'server': {
                    'host': '0.0.0.0',
                    'api_port': 5000,
                    'federated_port': 50051,
                    'max_clients': 10,
                    'timeout': 300
                },
                'client': {
                    'reconnect_interval': 5,
                    'heartbeat_interval': 30,
                    'max_retries': 3
                },
                'mining': {
                    'default_threshold': 100,
                    'privacy_epsilon': 1.0,
                    'num_rounds': 3
                },
                'ui': {
                    'auto_open_browser': True,
                    'theme': 'dark'
                }
            }
            self._save_config(default_config)
            return default_config
    
    def _save_config(self, config: Dict):
        """Save system configuration"""
        with open('integrated_config.json', 'w') as f:
            json.dump(config, f, indent=2)
    
    def start_server_mode(self):
        """Start the system in server mode"""
        logger.info("Starting Integrated System in SERVER mode")
        
        # Initialize Flask API server
        self.flask_app = Flask(__name__)
        CORS(self.flask_app)
        self.socketio = SocketIO(self.flask_app, cors_allowed_origins="*")
        
        # Initialize API state
        self.api_state = self._initialize_api_state()
        
        # Setup Flask routes
        self._setup_flask_routes()
        
        # Setup WebSocket events
        self._setup_websocket_events()
        
        # Start federated learning server
        self._start_federated_server()
        
        # Start Flask server
        self._start_flask_server()
        
        # Wait a moment for servers to start
        time.sleep(2)
        
        # Open browser
        if self.config['ui']['auto_open_browser']:
            webbrowser.open(f'http://localhost:{self.api_port}')
        
        logger.info(f"Server mode started successfully")
        logger.info(f"API Server: http://localhost:{self.api_port}")
        logger.info(f"Federated Server: {self.host}:{self.federated_port}")
        
        # Keep the main thread alive
        self.running = True
        while self.running:
            time.sleep(1)
    
    def start_client_mode(self):
        """Start the system in client mode"""
        logger.info("Starting Integrated System in CLIENT mode")
        
        if not self.server_address:
            logger.error("Server address required for client mode")
            return False
        
        # Initialize federated client
        self.federated_client = FederatedLearningClient(
            client_id=self.client_id,
            server_address=self.server_address,
            server_port=self.federated_port,
            min_utility_threshold=self.config['mining']['default_threshold'],
            epsilon=self.config['mining']['privacy_epsilon']
        )
        
        # Connect to server
        if not self.federated_client.connect_to_server():
            logger.error("Failed to connect to federated server")
            return False
        
        # Register with server
        if not self.federated_client.register_with_server():
            logger.error("Failed to register with federated server")
            return False
        
        # Start client operations
        self._start_client_operations()
        
        logger.info(f"Client mode started successfully")
        logger.info(f"Connected to server: {self.server_address}:{self.federated_port}")
        return True

    def _initialize_api_state(self) -> Dict:
        """Initialize API state for server mode"""
        return {
            'clients': {
                'client-1': {
                    'id': 'client-1',
                    'name': 'Electronics Store',
                    'type': 'electronics',
                    'status': 'healthy',
                    'lastUpdate': datetime.now().isoformat(),
                    'dataQuality': 0.95,
                    'contributionScore': 0.87,
                    'networkLatency': 45,
                    'localAccuracy': 0.92,
                    'transactionCount': 1250,
                    'patterns': 23
                },
                'client-2': {
                    'id': 'client-2',
                    'name': 'Fashion Store',
                    'type': 'fashion',
                    'status': 'healthy',
                    'lastUpdate': datetime.now().isoformat(),
                    'dataQuality': 0.91,
                    'contributionScore': 0.82,
                    'networkLatency': 52,
                    'localAccuracy': 0.89,
                    'transactionCount': 980,
                    'patterns': 18
                },
                'client-3': {
                    'id': 'client-3',
                    'name': 'Home & Garden Store',
                    'type': 'garden',
                    'status': 'healthy',
                    'lastUpdate': datetime.now().isoformat(),
                    'dataQuality': 0.88,
                    'contributionScore': 0.79,
                    'networkLatency': 38,
                    'localAccuracy': 0.91,
                    'transactionCount': 756,
                    'patterns': 15
                }
            },
            'transactions': {},
            'items': {},
            'patterns': {},
            'global_patterns': [],
            'recommendations': {},
            'mining_jobs': {},
            'federation_status': {
                'round': 0,
                'progress': 0.0,
                'participatingClients': 0,
                'totalClients': 0,
                'convergenceStatus': 'waiting',
                'eta': 'N/A'
            }
        }
    
    def _setup_flask_routes(self):
        """Setup Flask API routes"""
        
        @self.flask_app.route('/')
        def serve_index():
            return send_from_directory('.', 'index.html')
        
        @self.flask_app.route('/<path:filename>')
        def serve_static(filename):
            return send_from_directory('.', filename)
        
        @self.flask_app.route('/api/health', methods=['GET'])
        def health_check():
            return jsonify({
                'status': 'healthy',
                'mode': self.mode,
                'timestamp': datetime.now().isoformat(),
                'federated_server': self.federated_server is not None if self.mode == 'server' else None,
                'federated_client': self.federated_client is not None if self.mode == 'client' else None
            })
        
        @self.flask_app.route('/api/clients/<client_id>/transactions', methods=['GET'])
        def get_client_transactions(client_id):
            if client_id not in self.api_state['transactions']:
                self.api_state['transactions'][client_id] = []
            return jsonify(self.api_state['transactions'][client_id])
        
        @self.flask_app.route('/api/clients/<client_id>/transactions', methods=['POST'])
        def create_client_transaction(client_id):
            data = request.get_json()
            transaction_id = f"tx_{len(self.api_state['transactions'].get(client_id, [])) + 1}"
            data['id'] = transaction_id
            data['created_at'] = datetime.now().isoformat()
            
            if client_id not in self.api_state['transactions']:
                self.api_state['transactions'][client_id] = []
            
            self.api_state['transactions'][client_id].append(data)
            return jsonify(data)
        
        @self.flask_app.route('/api/clients/<client_id>/items', methods=['GET'])
        def get_client_items(client_id):
            if client_id not in self.api_state['items']:
                self.api_state['items'][client_id] = []
            return jsonify(self.api_state['items'][client_id])
        
        @self.flask_app.route('/api/clients/<client_id>/items', methods=['POST'])
        def create_client_item(client_id):
            data = request.get_json()
            if client_id not in self.api_state['items']:
                self.api_state['items'][client_id] = []
            
            item = {
                'id': f"item_{len(self.api_state['items'][client_id])}",
                'name': data.get('name', ''),
                'category': data.get('category', ''),
                'utility': data.get('utility', 0),
                'timestamp': datetime.now().isoformat()
            }
            
            self.api_state['items'][client_id].append(item)
            return jsonify(item), 201
        
        @self.flask_app.route('/api/clients/<client_id>/mining/start', methods=['POST'])
        def start_client_mining(client_id):
            data = request.get_json()
            threshold = data.get('threshold', get_min_utility_threshold())
            
            # Update threshold if provided
            if 'threshold' in data:
                set_min_utility_threshold(threshold)
            
            job_id = f"job_{client_id}_{int(time.time())}"
            
            # Start mining in background thread
            def run_mining():
                try:
                    if BACKEND_AVAILABLE:
                        # Use real HUI mining
                        miner = HUIMiner(min_utility_threshold=threshold)
                        # Add your dataset processing here
                        # For now, use dummy data - in real implementation, load actual transactions
                        dummy_transactions = [
                            [('item1', 2, 10), ('item2', 1, 15)],
                            [('item1', 1, 10), ('item3', 3, 20)],
                            [('item2', 2, 15), ('item3', 1, 20)]
                        ]
                        # Create dummy header table for testing
                        dummy_header = {'item1': None, 'item2': None, 'item3': None}
                        results = miner.mine_huis_pseudo_projection(dummy_header)
                        # Convert results to expected format
                        formatted_results = []
                        for itemset in results:
                            if isinstance(itemset, frozenset):
                                formatted_results.append({
                                    'itemset': list(itemset),
                                    'utility': 150,  # Dummy utility
                                    'support': 0.5   # Dummy support
                                })
                        results = formatted_results
                    else:
                        # Simulate mining
                        time.sleep(2)
                        results = [{'itemset': ['item1', 'item2'], 'utility': 150}]
                    
                    self.api_state['mining_jobs'][job_id] = {
                        'status': 'completed',
                        'results': results,
                        'completed_at': datetime.now().isoformat()
                    }
                    
                    # Update patterns
                    if client_id not in self.api_state['patterns']:
                        self.api_state['patterns'][client_id] = []
                    self.api_state['patterns'][client_id].extend(results)
                    
                except Exception as e:
                    logger.error(f"Mining error: {e}")
                    self.api_state['mining_jobs'][job_id] = {
                        'status': 'failed',
                        'error': str(e),
                        'completed_at': datetime.now().isoformat()
                    }
            
            self.api_state['mining_jobs'][job_id] = {
                'status': 'running',
                'started_at': datetime.now().isoformat(),
                'threshold': threshold
            }
            
            threading.Thread(target=run_mining, daemon=True).start()
            
            return jsonify({
                'job_id': job_id,
                'status': 'started',
                'threshold': threshold
            })
        
        @self.flask_app.route('/api/clients/<client_id>/mining/<job_id>/status', methods=['GET'])
        def get_mining_status(client_id, job_id):
            if job_id in self.api_state['mining_jobs']:
                return jsonify(self.api_state['mining_jobs'][job_id])
            return jsonify({'error': 'Job not found'}), 404
        
        @self.flask_app.route('/api/federation/status', methods=['GET'])
        def get_federation_status():
            if self.mode == 'server' and self.federated_server:
                stats = self.federated_server.get_server_stats()
                self.api_state['federation_status'].update(stats)
            return jsonify(self.api_state['federation_status'])
        
        @self.flask_app.route('/api/federation/clients', methods=['GET'])
        def get_federation_clients():
            return jsonify(list(self.api_state['clients'].values()))
        
        @self.flask_app.route('/api/federation/patterns', methods=['GET'])
        def get_global_patterns():
            if self.mode == 'server' and self.federated_server:
                # Get patterns from federated server
                patterns = self.federated_server._aggregate_itemsets()
                return jsonify(patterns)
            return jsonify(self.api_state['global_patterns'])
        
        @self.flask_app.route('/api/federation/trigger-round', methods=['POST'])
        def trigger_federation_round():
            if self.mode == 'server' and self.federated_server:
                # Trigger federated learning round
                # This would integrate with your federated learning logic
                return jsonify({'status': 'round_triggered'})
            return jsonify({'error': 'Server mode required'}), 400
    
    def _setup_websocket_events(self):
        """Setup WebSocket events"""
        
        @self.socketio.on('connect')
        def handle_connect():
            logger.info(f"Client connected: {request.sid}")
            emit('connected', {'message': 'Connected to Integrated System'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            logger.info(f"Client disconnected: {request.sid}")
        
        @self.socketio.on('join_room')
        def handle_join_room(data):
            room = data.get('room', 'default')
            join_room(room)
            emit('joined_room', {'room': room})
        
        @self.socketio.on('request_update')
        def handle_request_update(data):
            update_type = data.get('type', 'general')
            if update_type == 'federation_status':
                emit('federation_update', self.api_state['federation_status'])
            elif update_type == 'clients':
                emit('clients_update', list(self.api_state['clients'].values()))
    
    def _start_federated_server(self):
        """Start federated learning server"""
        try:
            self.federated_server = FederatedLearningServer(
                min_utility_threshold=self.config['mining']['default_threshold'],
                epsilon=self.config['mining']['privacy_epsilon'],
                num_rounds=self.config['mining']['num_rounds']
            )
            
            def run_federated_server():
                serve_federated(
                    host=self.host,
                    port=self.federated_port,
                    min_utility_threshold=self.config['mining']['default_threshold'],
                    epsilon=self.config['mining']['privacy_epsilon'],
                    num_rounds=self.config['mining']['num_rounds']
                )
            
            self.federated_thread = threading.Thread(target=run_federated_server, daemon=True)
            self.federated_thread.start()
            
            logger.info(f"Federated server started on {self.host}:{self.federated_port}")
            
        except Exception as e:
            logger.error(f"Failed to start federated server: {e}")
    
    def _start_flask_server(self):
        """Start Flask API server in a separate thread"""
        def run_flask_server():
            try:
                self.socketio.run(
                    self.flask_app,
                    host=self.host,
                    port=self.api_port,
                    debug=False,
                    use_reloader=False
                )
            except Exception as e:
                logger.error(f"Failed to start Flask server: {e}")
        
        self.server_thread = threading.Thread(target=run_flask_server, daemon=True)
        self.server_thread.start()
    
    def _start_client_operations(self):
        """Start client operations"""
        def run_client_operations():
            while self.running:
                try:
                    # Health check
                    if self.federated_client:
                        self.federated_client.health_check()
                    
                    # Load local data if available
                    if hasattr(self.federated_client, 'load_local_data'):
                        self.federated_client.load_local_data()
                    
                    time.sleep(self.config['client']['heartbeat_interval'])
                    
                except Exception as e:
                    logger.error(f"Client operation error: {e}")
                    time.sleep(self.config['client']['reconnect_interval'])
        
        self.running = True
        self.client_thread = threading.Thread(target=run_client_operations, daemon=True)
        self.client_thread.start()
    
    def stop(self):
        """Stop the integrated system"""
        logger.info("Stopping Integrated System")
        self.running = False
        
        if self.federated_client:
            self.federated_client.close()
        
        # Stop Flask server
        if self.flask_app:
            # This would need proper Flask shutdown handling
            pass
        
        logger.info("Integrated System stopped")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Integrated FP-Growth Federated Learning System')
    parser.add_argument('--mode', choices=['server', 'client'], default='server',
                       help='Run mode: server or client')
    parser.add_argument('--host', default='0.0.0.0', help='Host address')
    parser.add_argument('--api-port', type=int, default=5000, help='API server port')
    parser.add_argument('--federated-port', type=int, default=50051, help='Federated server port')
    parser.add_argument('--client-id', help='Client ID (required for client mode)')
    parser.add_argument('--server-address', help='Server address (required for client mode)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.mode == 'client':
        if not args.client_id:
            print("Error: --client-id is required for client mode")
            sys.exit(1)
        if not args.server_address:
            print("Error: --server-address is required for client mode")
            sys.exit(1)
    
    # Create and start integrated system
    system = IntegratedSystem(
        mode=args.mode,
        host=args.host,
        api_port=args.api_port,
        federated_port=args.federated_port,
        client_id=args.client_id,
        server_address=args.server_address
    )
    
    try:
        if args.mode == 'server':
            print(f"Starting server on {args.host}:{args.api_port}")
            print("Press Ctrl+C to stop")
            system.start_server_mode()
        else:
            if system.start_client_mode():
                print(f"Client {args.client_id} connected to server {args.server_address}")
                print("Press Ctrl+C to stop")
                while True:
                    time.sleep(1)
            else:
                print("Failed to start client mode")
                sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        system.stop()

if __name__ == '__main__':
    main() 