import grpc
import time
import threading
import uuid
import logging
from typing import List, Dict, Set, Tuple
import numpy as np
from cryptography.fernet import Fernet
import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from preprocessor import construct_pruned_item_list
from fp_tree_builder import construct_huim_fp_tree
from hui_miner import HUIMiner
from privacy_wrapper import PrivacyPreservingHUIMining
from data_parser import DataProcessor

import federated_learning_pb2
import federated_learning_pb2_grpc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FederatedLearningClient:
    """
    Federated Learning Client for High-Utility Itemset Mining
    Runs local FP-Growth and communicates with the federated server
    """
    
    def __init__(self, client_id: str, server_address: str, server_port: int, 
                 dataset_path: str = None, min_utility_threshold: float = 50, 
                 epsilon: float = 1.0):
        self.client_id = client_id
        self.server_address = server_address
        self.server_port = server_port
        self.dataset_path = dataset_path
        self.min_utility_threshold = min_utility_threshold
        self.epsilon = epsilon
        
        # Session management
        self.session_id = None
        self.registered = False
        self.current_round = 0
        
        # Local data and results
        self.transactions = []
        self.external_utility = {}
        self.local_itemsets = []
        
        # gRPC channel and stub
        self.channel = None
        self.stub = None
        
        # Privacy and security
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Thread safety
        self.lock = threading.Lock()
        
        logger.info(f"Federated Learning Client {client_id} initialized")
    
    def connect_to_server(self):
        """Establish connection to the federated learning server"""
        try:
            server_url = f"{self.server_address}:{self.server_port}"
            self.channel = grpc.insecure_channel(server_url)
            self.stub = federated_learning_pb2_grpc.FederatedLearningServiceStub(self.channel)
            
            logger.info(f"Connected to server at {server_url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to server: {e}")
            return False
    
    def register_with_server(self, client_address: str = "localhost", client_port: int = 0):
        """Register this client with the federated learning server"""
        try:
            if not self.stub:
                logger.error("Not connected to server")
                return False
            
            # Prepare registration request
            capabilities = ["fp_growth", "hui_mining", "privacy_preserving"]
            registration_request = federated_learning_pb2.ClientRegistration(
                client_id=self.client_id,
                client_address=client_address,
                port=client_port,
                capabilities=capabilities
            )
            
            # Send registration request
            response = self.stub.RegisterClient(registration_request)
            
            if response.success:
                self.session_id = response.session_id
                self.registered = True
                
                # Update configuration from server
                config = response.config
                self.min_utility_threshold = config.min_utility_threshold
                self.epsilon = config.epsilon
                
                logger.info(f"Successfully registered with server. Session: {self.session_id}")
                logger.info(f"Server config: threshold={self.min_utility_threshold}, epsilon={self.epsilon}")
                return True
            else:
                logger.error(f"Registration failed: {response.message}")
                return False
                
        except Exception as e:
            logger.error(f"Error during registration: {e}")
            return False
    
    def load_local_data(self):
        """Load and prepare local data for mining"""
        try:
            if not self.dataset_path:
                logger.warning("No dataset path provided, using sample data")
                self._load_sample_data()
                return True
            
            # Load data using existing DataProcessor
            processor = DataProcessor(self.dataset_path)
            self.transactions = processor.load_foodmart_transactions_as_tuple()
            
            if not self.transactions:
                logger.error("Failed to load transactions")
                return False
            
            self.external_utility = processor.get_dummy_foodmart_item_utilities()
            
            logger.info(f"Loaded {len(self.transactions)} transactions and {len(self.external_utility)} item utilities")
            return True
            
        except Exception as e:
            logger.error(f"Error loading local data: {e}")
            return False
    
    def _load_sample_data(self):
        """Load sample data for testing"""
        # Sample transaction database with (item_id, quantity, utility) format
        self.transactions = [
            [("rice", 2, 10), ("egg", 1, 6), ("sugar", 1, 4)],
            [("rice", 1, 5), ("sugar", 3, 12)],
            [("egg", 2, 12), ("sugar", 2, 8)],
            [("rice", 3, 15), ("egg", 1, 6)],
            [("milk", 2, 8), ("bread", 1, 3)],
            [("milk", 1, 4), ("bread", 2, 6), ("butter", 1, 6)]
        ]
        
        # Sample external utilities
        self.external_utility = {
            "rice": 5, "egg": 3, "sugar": 2, 
            "milk": 4, "bread": 3, "butter": 6
        }
        
        logger.info("Loaded sample data")
    
    def run_local_mining(self):
        """Run local FP-Growth mining on local data"""
        try:
            if not self.transactions:
                logger.error("No transactions loaded")
                return False
            
            logger.info("Starting local FP-Growth mining...")
            
            # Step 1: Prune low-utility items
            sorted_items = construct_pruned_item_list(
                self.transactions, 
                self.min_utility_threshold, 
                self.external_utility
            )
            logger.info(f"Pruned items, {len(sorted_items)} high-utility items remaining")
            
            # Step 2: Construct FP-Tree
            root, header_table = construct_huim_fp_tree(
                self.transactions, 
                sorted_items, 
                self.external_utility
            )
            logger.info("FP-Tree constructed successfully")
            
            # Step 3: Mine high-utility itemsets
            miner = HUIMiner(self.external_utility, self.min_utility_threshold)
            huis = miner.mine_huis_pseudo_projection(header_table, root)
            
            # Convert to list format for easier processing
            self.local_itemsets = []
            for itemset in huis:
                items = list(itemset)
                # Calculate utility and support
                utility = self._calculate_itemset_utility(items)
                support = self._calculate_itemset_support(items)
                
                self.local_itemsets.append({
                    'itemset': itemset,
                    'items': items,
                    'utility': utility,
                    'support': support
                })
            
            logger.info(f"Local mining completed: {len(self.local_itemsets)} high-utility itemsets found")
            return True
            
        except Exception as e:
            logger.error(f"Error during local mining: {e}")
            return False
    
    def run_privacy_preserving_mining(self):
        """Run privacy-preserving mining using existing wrapper"""
        try:
            if not self.transactions:
                logger.error("No transactions loaded")
                return False
            
            logger.info("Starting privacy-preserving mining...")
            
            # Convert transactions to the format expected by privacy wrapper
            transactions_list = []
            for tx in self.transactions:
                if isinstance(tx[0], tuple):
                    # Convert (item, quantity, utility) tuples to {item: quantity} format
                    tx_dict = {item: quantity for item, quantity, _ in tx}
                else:
                    tx_dict = tx
                transactions_list.append(tx_dict)
            
            # Run privacy-preserving mining
            private_huis = PrivacyPreservingHUIMining.privacy_preserving_hui_mining_algorithm8(
                transactions_list=transactions_list,
                item_utils_dict=self.external_utility,
                minutil_threshold=self.min_utility_threshold,
                epsilon=self.epsilon,
                num_mpc_workers=3
            )
            
            # Convert results to standard format
            self.local_itemsets = []
            for itemset in private_huis:
                if isinstance(itemset, frozenset):
                    items = list(itemset)
                else:
                    items = list(itemset)
                
                utility = self._calculate_itemset_utility(items)
                support = self._calculate_itemset_support(items)
                
                self.local_itemsets.append({
                    'itemset': frozenset(items),
                    'items': items,
                    'utility': utility,
                    'support': support
                })
            
            logger.info(f"Privacy-preserving mining completed: {len(self.local_itemsets)} itemsets found")
            return True
            
        except Exception as e:
            logger.error(f"Error during privacy-preserving mining: {e}")
            return False
    
    def send_results_to_server(self):
        """Send local mining results to the federated server"""
        try:
            if not self.registered or not self.session_id:
                logger.error("Not registered with server")
                return False
            
            if not self.local_itemsets:
                logger.error("No local results to send")
                return False
            
            # Prepare itemsets for transmission
            itemsets_proto = []
            local_utility_sum = 0.0
            
            for itemset_data in self.local_itemsets:
                itemset_proto = federated_learning_pb2.HighUtilityItemset(
                    items=itemset_data['items'],
                    utility=itemset_data['utility'],
                    support=itemset_data['support']
                )
                itemsets_proto.append(itemset_proto)
                local_utility_sum += itemset_data['utility']
            
            # Encrypt sensitive data (optional)
            encrypted_data = self.cipher_suite.encrypt(str(self.transactions).encode())
            
            # Prepare local results
            local_results = federated_learning_pb2.LocalResults(
                client_id=self.client_id,
                session_id=self.session_id,
                itemsets=itemsets_proto,
                local_utility_sum=local_utility_sum,
                transaction_count=len(self.transactions),
                encrypted_data=encrypted_data
            )
            
            # Send to server
            response = self.stub.SendLocalResults(local_results)
            
            if response.success:
                self.current_round = response.round_number
                logger.info(f"Results sent successfully to server. Round: {self.current_round}")
                return True
            else:
                logger.error(f"Failed to send results: {response.message}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending results to server: {e}")
            return False
    
    def get_global_results(self):
        """Request and receive global aggregated results from server"""
        try:
            if not self.registered or not self.session_id:
                logger.error("Not registered with server")
                return None
            
            # Prepare request
            request = federated_learning_pb2.GlobalResultsRequest(
                client_id=self.client_id,
                session_id=self.session_id
            )
            
            # Get global results
            response = self.stub.GetGlobalResults(request)
            
            logger.info(f"Received global results: {len(response.global_itemsets)} itemsets")
            logger.info(f"Global utility sum: {response.global_utility_sum}")
            logger.info(f"Total transactions: {response.total_transactions}")
            logger.info(f"Participating clients: {response.participating_clients}")
            logger.info(f"Privacy budget used: {response.privacy_budget_used}")
            
            # Convert to local format
            global_itemsets = []
            for itemset_proto in response.global_itemsets:
                itemset_data = {
                    'itemset': frozenset(itemset_proto.items),
                    'items': list(itemset_proto.items),
                    'utility': itemset_proto.utility,
                    'support': itemset_proto.support
                }
                global_itemsets.append(itemset_data)
            
            return global_itemsets
            
        except Exception as e:
            logger.error(f"Error getting global results: {e}")
            return None
    
    def health_check(self):
        """Send health check to server"""
        try:
            if not self.stub:
                return False
            
            request = federated_learning_pb2.HealthRequest(client_id=self.client_id)
            response = self.stub.HealthCheck(request)
            
            if response.healthy:
                logger.debug("Health check passed")
                return True
            else:
                logger.warning(f"Health check failed: {response.status}")
                return False
                
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return False
    
    def _calculate_itemset_utility(self, items: List[str]) -> float:
        """Calculate utility of an itemset"""
        try:
            utility = 0.0
            for item in items:
                utility += self.external_utility.get(item, 0)
            return utility
        except Exception:
            return 0.0
    
    def _calculate_itemset_support(self, items: List[str]) -> float:
        """Calculate support (frequency) of an itemset"""
        try:
            support = 0
            for tx in self.transactions:
                tx_items = set()
                for item, _ in tx:
                    tx_items.add(item)
                
                if all(item in tx_items for item in items):
                    support += 1
            
            return support / len(self.transactions) if self.transactions else 0.0
        except Exception:
            return 0.0
    
    def run_federated_learning(self, use_privacy_preserving: bool = True):
        """Run the complete federated learning process"""
        try:
            logger.info("Starting federated learning process...")
            
            # Step 1: Connect to server
            if not self.connect_to_server():
                return False
            
            # Step 2: Register with server
            if not self.register_with_server():
                return False
            
            # Step 3: Load local data
            if not self.load_local_data():
                return False
            
            # Step 4: Run local mining
            if use_privacy_preserving:
                success = self.run_privacy_preserving_mining()
            else:
                success = self.run_local_mining()
            
            if not success:
                return False
            
            # Step 5: Send results to server
            if not self.send_results_to_server():
                return False
            
            # Step 6: Get global results
            global_results = self.get_global_results()
            if global_results:
                logger.info("Federated learning completed successfully!")
                return True
            else:
                logger.error("Failed to get global results")
                return False
                
        except Exception as e:
            logger.error(f"Error in federated learning process: {e}")
            return False
    
    def close(self):
        """Close the client connection"""
        try:
            if self.channel:
                self.channel.close()
            logger.info("Client connection closed")
        except Exception as e:
            logger.error(f"Error closing client: {e}")

def main():
    """Main function to run the federated learning client"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Federated Learning Client for HUI Mining')
    parser.add_argument('--client-id', required=True, help='Unique client ID')
    parser.add_argument('--server-address', default='localhost', help='Server address')
    parser.add_argument('--server-port', type=int, default=50051, help='Server port')
    parser.add_argument('--dataset-path', help='Path to local dataset')
    parser.add_argument('--threshold', type=float, default=50, help='Minimum utility threshold')
    parser.add_argument('--epsilon', type=float, default=1.0, help='Privacy budget')
    parser.add_argument('--use-privacy', action='store_true', help='Use privacy-preserving mining')
    
    args = parser.parse_args()
    
    # Create and run client
    client = FederatedLearningClient(
        client_id=args.client_id,
        server_address=args.server_address,
        server_port=args.server_port,
        dataset_path=args.dataset_path,
        min_utility_threshold=args.threshold,
        epsilon=args.epsilon
    )
    
    try:
        success = client.run_federated_learning(use_privacy_preserving=args.use_privacy)
        if success:
            logger.info("Federated learning completed successfully!")
        else:
            logger.error("Federated learning failed!")
    finally:
        client.close()

if __name__ == '__main__':
    main() 