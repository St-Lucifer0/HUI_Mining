import grpc
import time
import threading
import uuid
from concurrent import futures
from collections import defaultdict, Counter
import logging
from typing import Dict, List, Set, Tuple
import numpy as np
from cryptography.fernet import Fernet
import os

import federated_learning_pb2
import federated_learning_pb2_grpc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FederatedLearningServer(federated_learning_pb2_grpc.FederatedLearningServiceServicer):
    """
    Federated Learning Server for High-Utility Itemset Mining
    Aggregates results from multiple clients while preserving privacy
    """
    
    def __init__(self, min_utility_threshold=50, epsilon=1.0, num_rounds=3, output_formatter=None):
        self.min_utility_threshold = min_utility_threshold
        self.epsilon = epsilon
        self.num_rounds = num_rounds
        
        # Session management
        self.sessions: Dict[str, Dict] = {}
        self.clients: Dict[str, Dict] = {}
        
        # Results storage
        self.local_results: Dict[str, List] = defaultdict(list)
        self.global_itemsets: Set[frozenset] = set()
        self.global_utility_sum = 0.0
        self.total_transactions = 0
        self.participating_clients = 0
        
        # Privacy and security
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Round management
        self.current_round = 0
        self.round_results: Dict[int, List] = defaultdict(list)
        
        # Output formatting
        self.output_formatter = output_formatter
        
        # Thread safety
        self.lock = threading.Lock()
        
        logger.info(f"Federated Learning Server initialized with threshold={min_utility_threshold}, epsilon={epsilon}")
    
    def RegisterClient(self, request, context):
        """Register a new client for federated learning"""
        try:
            with self.lock:
                client_id = request.client_id
                session_id = str(uuid.uuid4())
                
                # Create client record
                self.clients[client_id] = {
                    'address': request.client_address,
                    'port': request.port,
                    'capabilities': list(request.capabilities),
                    'session_id': session_id,
                    'registered_at': time.time(),
                    'last_seen': time.time()
                }
                
                # Create session
                self.sessions[session_id] = {
                    'client_id': client_id,
                    'created_at': time.time(),
                    'round': 0,
                    'status': 'active'
                }
                
                # Global configuration
                config = federated_learning_pb2.GlobalConfig(
                    min_utility_threshold=self.min_utility_threshold,
                    epsilon=self.epsilon,
                    num_rounds=self.num_rounds,
                    timeout_seconds=300
                )
                
                logger.info(f"Client {client_id} registered with session {session_id}")
                
                return federated_learning_pb2.RegistrationResponse(
                    success=True,
                    message=f"Successfully registered client {client_id}",
                    session_id=session_id,
                    config=config
                )
                
        except Exception as e:
            logger.error(f"Error registering client: {e}")
            return federated_learning_pb2.RegistrationResponse(
                success=False,
                message=f"Registration failed: {str(e)}"
            )
    
    def SendLocalResults(self, request, context):
        """Receive and process local results from clients"""
        try:
            with self.lock:
                client_id = request.client_id
                session_id = request.session_id
                
                # Validate session
                if session_id not in self.sessions:
                    return federated_learning_pb2.ServerAcknowledgment(
                        success=False,
                        message="Invalid session ID"
                    )
                
                # Update client last seen
                if client_id in self.clients:
                    self.clients[client_id]['last_seen'] = time.time()
                
                # Process local results
                local_itemsets = []
                for itemset_proto in request.itemsets:
                    itemset = frozenset(itemset_proto.items)
                    local_itemsets.append({
                        'itemset': itemset,
                        'utility': itemset_proto.utility,
                        'support': itemset_proto.support
                    })
                
                # Store results for current round
                self.round_results[self.current_round].append({
                    'client_id': client_id,
                    'itemsets': local_itemsets,
                    'local_utility_sum': request.local_utility_sum,
                    'transaction_count': request.transaction_count,
                    'encrypted_data': request.encrypted_data
                })
                
                # Update global statistics
                self.global_utility_sum += request.local_utility_sum
                self.total_transactions += request.transaction_count
                
                # Add to output formatter if available
                if self.output_formatter:
                    client_stats = {
                        'local_utility_sum': request.local_utility_sum,
                        'transaction_count': request.transaction_count
                    }
                    self.output_formatter.add_client_results(client_id, local_itemsets, client_stats)
                
                logger.info(f"Received results from client {client_id}: {len(local_itemsets)} itemsets")
                
                return federated_learning_pb2.ServerAcknowledgment(
                    success=True,
                    message=f"Results received from {client_id}",
                    round_number=self.current_round
                )
                
        except Exception as e:
            logger.error(f"Error processing local results: {e}")
            return federated_learning_pb2.ServerAcknowledgment(
                success=False,
                message=f"Failed to process results: {str(e)}"
            )
    
    def GetGlobalResults(self, request, context):
        """Provide aggregated global results to clients"""
        try:
            with self.lock:
                client_id = request.client_id
                session_id = request.session_id
                
                # Validate session
                if session_id not in self.sessions:
                    return federated_learning_pb2.GlobalResults(
                        global_itemsets=[],
                        global_utility_sum=0.0,
                        total_transactions=0,
                        participating_clients=0,
                        privacy_budget_used=0.0
                    )
                
                # Aggregate results from all rounds
                aggregated_itemsets = self._aggregate_itemsets()
                
                # Convert to protobuf format
                global_itemsets_proto = []
                for itemset_data in aggregated_itemsets:
                    itemset_proto = federated_learning_pb2.HighUtilityItemset(
                        items=list(itemset_data['itemset']),
                        utility=itemset_data['utility'],
                        support=itemset_data['support']
                    )
                    global_itemsets_proto.append(itemset_proto)
                
                # Calculate privacy budget used
                privacy_budget_used = self._calculate_privacy_budget_used()
                
                # Prepare server stats
                server_stats = {
                    'total_transactions': self.total_transactions,
                    'participating_clients': len(self.clients),
                    'global_utility_sum': self.global_utility_sum,
                    'privacy_budget_used': privacy_budget_used
                }
                
                # Add to output formatter if available
                if self.output_formatter:
                    self.output_formatter.add_global_results(aggregated_itemsets, server_stats)
                    
                    # Save results in all formats
                    try:
                        results_files = self.output_formatter.save_all_formats()
                        logger.info(f"Results saved to files: {list(results_files.values())}")
                        
                        # Print console summary
                        self.output_formatter.print_console_summary()
                    except Exception as e:
                        logger.warning(f"Failed to save output files: {e}")
                
                logger.info(f"Providing global results to {client_id}: {len(global_itemsets_proto)} itemsets")
                
                return federated_learning_pb2.GlobalResults(
                    global_itemsets=global_itemsets_proto,
                    global_utility_sum=self.global_utility_sum,
                    total_transactions=self.total_transactions,
                    participating_clients=len(self.clients),
                    privacy_budget_used=privacy_budget_used
                )
                
        except Exception as e:
            logger.error(f"Error providing global results: {e}")
            return federated_learning_pb2.GlobalResults(
                global_itemsets=[],
                global_utility_sum=0.0,
                total_transactions=0,
                participating_clients=0,
                privacy_budget_used=0.0
            )
    
    def BroadcastGlobalModel(self, request, context):
        """Broadcast global model to clients (for future rounds)"""
        try:
            with self.lock:
                client_id = request.client_id
                
                # Update global model with received aggregated itemsets
                for itemset_proto in request.aggregated_itemsets:
                    itemset = frozenset(itemset_proto.items)
                    self.global_itemsets.add(itemset)
                
                # Update global threshold
                if request.aggregated_utility_threshold > 0:
                    self.min_utility_threshold = request.aggregated_utility_threshold
                
                # Update round
                if request.round_number > self.current_round:
                    self.current_round = request.round_number
                
                logger.info(f"Global model updated from {client_id}, round {request.round_number}")
                
                return federated_learning_pb2.ClientAcknowledgment(
                    client_id=client_id,
                    received=True,
                    message="Global model received successfully"
                )
                
        except Exception as e:
            logger.error(f"Error broadcasting global model: {e}")
            return federated_learning_pb2.ClientAcknowledgment(
                client_id=client_id,
                received=False,
                message=f"Failed to process global model: {str(e)}"
            )
    
    def HealthCheck(self, request, context):
        """Health check endpoint"""
        try:
            client_id = request.client_id
            
            # Update client last seen
            if client_id in self.clients:
                self.clients[client_id]['last_seen'] = time.time()
            
            return federated_learning_pb2.HealthResponse(
                healthy=True,
                status="Server is healthy",
                timestamp=int(time.time())
            )
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return federated_learning_pb2.HealthResponse(
                healthy=False,
                status=f"Server error: {str(e)}",
                timestamp=int(time.time())
            )
    
    def _aggregate_itemsets(self) -> List[Dict]:
        """Aggregate itemsets from all clients with privacy preservation"""
        try:
            # Collect all itemsets from all rounds
            all_itemsets = []
            for round_results in self.round_results.values():
                for client_result in round_results:
                    all_itemsets.extend(client_result['itemsets'])
            
            # Group by itemset
            itemset_groups = defaultdict(list)
            for itemset_data in all_itemsets:
                itemset_groups[itemset_data['itemset']].append(itemset_data)
            
            # Aggregate each itemset
            aggregated_itemsets = []
            for itemset, group in itemset_groups.items():
                # Calculate aggregated utility (with noise for privacy)
                utilities = [item['utility'] for item in group]
                supports = [item['support'] for item in group]
                
                # Add Laplace noise for differential privacy
                noise_scale = 1.0 / self.epsilon
                utility_noise = np.random.laplace(0, noise_scale)
                support_noise = np.random.laplace(0, noise_scale)
                
                aggregated_utility = sum(utilities) + utility_noise
                aggregated_support = sum(supports) + support_noise
                
                # Only include if above threshold
                if aggregated_utility >= self.min_utility_threshold:
                    aggregated_itemsets.append({
                        'itemset': itemset,
                        'utility': max(0, aggregated_utility),  # Ensure non-negative
                        'support': max(0, aggregated_support)
                    })
            
            # Sort by utility (descending)
            aggregated_itemsets.sort(key=lambda x: x['utility'], reverse=True)
            
            return aggregated_itemsets
            
        except Exception as e:
            logger.error(f"Error aggregating itemsets: {e}")
            return []
    
    def _calculate_privacy_budget_used(self) -> float:
        """Calculate the privacy budget used so far"""
        try:
            # Simple calculation based on number of rounds and epsilon
            return self.current_round * self.epsilon
        except Exception as e:
            logger.error(f"Error calculating privacy budget: {e}")
            return 0.0
    
    def get_server_stats(self) -> Dict:
        """Get server statistics for monitoring"""
        with self.lock:
            return {
                'registered_clients': len(self.clients),
                'active_sessions': len(self.sessions),
                'current_round': self.current_round,
                'total_transactions': self.total_transactions,
                'global_utility_sum': self.global_utility_sum,
                'global_itemsets_count': len(self.global_itemsets)
            }

def serve(host='0.0.0.0', port=50051, min_utility_threshold=50, epsilon=1.0, num_rounds=3):
    """Start the federated learning server"""
    # Import output formatter
    try:
        from output_formatter import FederatedLearningOutputFormatter
        output_formatter = FederatedLearningOutputFormatter()
        logger.info("Output formatter initialized - results will be saved to files")
    except ImportError:
        output_formatter = None
        logger.warning("Output formatter not available - results will only be displayed in console")
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    federated_server = FederatedLearningServer(
        min_utility_threshold=min_utility_threshold,
        epsilon=epsilon,
        num_rounds=num_rounds,
        output_formatter=output_formatter
    )
    
    federated_learning_pb2_grpc.add_FederatedLearningServiceServicer_to_server(
        federated_server, server
    )
    
    server_address = f'{host}:{port}'
    server.add_insecure_port(server_address)
    server.start()
    
    logger.info(f"Federated Learning Server started on {server_address}")
    logger.info(f"Configuration: threshold={min_utility_threshold}, epsilon={epsilon}, rounds={num_rounds}")
    
    try:
        # Keep server running
        while True:
            time.sleep(1)
            # Print stats every 30 seconds
            if int(time.time()) % 30 == 0:
                stats = federated_server.get_server_stats()
                logger.info(f"Server Stats: {stats}")
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        server.stop(0)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Federated Learning Server for HUI Mining')
    parser.add_argument('--host', default='0.0.0.0', help='Server host')
    parser.add_argument('--port', type=int, default=50051, help='Server port')
    parser.add_argument('--threshold', type=float, default=50, help='Minimum utility threshold')
    parser.add_argument('--epsilon', type=float, default=1.0, help='Privacy budget')
    parser.add_argument('--rounds', type=int, default=3, help='Number of federated rounds')
    
    args = parser.parse_args()
    
    serve(
        host=args.host,
        port=args.port,
        min_utility_threshold=args.threshold,
        epsilon=args.epsilon,
        num_rounds=args.rounds
    ) 