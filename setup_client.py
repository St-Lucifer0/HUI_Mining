#!/usr/bin/env python3
"""
Client setup script for federated learning system
Run this on the laptops that will act as clients
"""

import os
import sys
import subprocess
import argparse
import logging
import time
import socket
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if required dependencies are installed"""
    logger.info("Checking dependencies...")
    
    # Check Python version
    if sys.version_info < (3, 9):
        logger.error("Python 3.9+ is required")
        return False
    
    # Check if pip is available
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      capture_output=True, check=True)
    except subprocess.CalledProcessError:
        logger.error("pip is not available")
        return False
    
    logger.info("Dependencies check passed")
    return True

def install_requirements():
    """Install Python requirements"""
    logger.info("Installing Python requirements...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        logger.info("Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install requirements: {e}")
        return False

def generate_grpc_code():
    """Generate gRPC code from protobuf"""
    logger.info("Generating gRPC code...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "grpc_tools.protoc",
            "-I.", "--python_out=.", "--grpc_python_out=.",
            "federated_learning.proto"
        ], check=True)
        logger.info("gRPC code generated successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to generate gRPC code: {e}")
        return False

def test_server_connection(server_address, server_port):
    """Test connection to the server"""
    logger.info(f"Testing connection to server {server_address}:{server_port}...")
    
    try:
        import grpc
        channel = grpc.insecure_channel(f"{server_address}:{server_port}")
        
        # Try to connect
        import federated_learning_pb2_grpc
        stub = federated_learning_pb2_grpc.FederatedLearningServiceStub(channel)
        
        # Simple health check
        import federated_learning_pb2
        request = federated_learning_pb2.HealthRequest(client_id="test")
        
        # Set a timeout
        import grpc
        response = stub.HealthCheck(request, timeout=5)
        
        if response.healthy:
            logger.info("Server connection successful!")
            return True
        else:
            logger.error(f"Server health check failed: {response.status}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to connect to server: {e}")
        return False

def create_client_config(client_id, server_address, server_port, dataset_path=None, 
                        threshold=50, epsilon=1.0, use_privacy=True):
    """Create client configuration file"""
    logger.info("Creating client configuration...")
    
    config = {
        "client_id": client_id,
        "server_address": server_address,
        "server_port": server_port,
        "dataset_path": dataset_path,
        "min_utility_threshold": threshold,
        "epsilon": epsilon,
        "use_privacy_preserving": use_privacy,
        "max_retries": 5,
        "retry_delay": 10
    }
    
    import json
    with open("client_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    logger.info("Client configuration created")
    return True

def run_client(client_id, server_address, server_port, dataset_path=None, 
               threshold=50, epsilon=1.0, use_privacy=True, auto_connect=True):
    """Run the federated learning client"""
    logger.info(f"Starting federated learning client: {client_id}")
    
    try:
        from federated_client import FederatedLearningClient
        
        client = FederatedLearningClient(
            client_id=client_id,
            server_address=server_address,
            server_port=server_port,
            dataset_path=dataset_path,
            min_utility_threshold=threshold,
            epsilon=epsilon
        )
        
        if auto_connect:
            # Test connection first
            if not test_server_connection(server_address, server_port):
                logger.error("Cannot connect to server. Please check:")
                logger.error("1. Server is running")
                logger.error("2. Network connection")
                logger.error("3. Firewall settings")
                logger.error("4. Server address and port")
                return False
        
        # Run federated learning
        success = client.run_federated_learning(use_privacy_preserving=use_privacy)
        
        if success:
            logger.info(f"Client {client_id} completed successfully!")
            return True
        else:
            logger.error(f"Client {client_id} failed!")
            return False
            
    except Exception as e:
        logger.error(f"Error running client: {e}")
        return False

def create_connection_test_script(server_address, server_port):
    """Create a simple script to test server connection"""
    script_content = f'''#!/usr/bin/env python3
import grpc
import federated_learning_pb2
import federated_learning_pb2_grpc

def test_connection():
    try:
        channel = grpc.insecure_channel('{server_address}:{server_port}')
        stub = federated_learning_pb2_grpc.FederatedLearningServiceStub(channel)
        
        request = federated_learning_pb2.HealthRequest(client_id="test")
        response = stub.HealthCheck(request, timeout=5)
        
        if response.healthy:
            print("✓ Connection to server successful!")
            return True
        else:
            print(f"✗ Server health check failed: {{response.status}}")
            return False
    except Exception as e:
        print(f"✗ Connection failed: {{e}}")
        return False

if __name__ == '__main__':
    test_connection()
'''
    
    with open("test_connection.py", "w") as f:
        f.write(script_content)
    
    logger.info("Connection test script created: test_connection.py")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Setup Federated Learning Client')
    parser.add_argument('--client-id', required=True, help='Unique client ID')
    parser.add_argument('--server-address', required=True, help='Server IP address')
    parser.add_argument('--server-port', type=int, default=50051, help='Server port (default: 50051)')
    parser.add_argument('--dataset-path', help='Path to local dataset file')
    parser.add_argument('--threshold', type=float, default=50, help='Utility threshold (default: 50)')
    parser.add_argument('--epsilon', type=float, default=1.0, help='Privacy budget (default: 1.0)')
    parser.add_argument('--no-privacy', action='store_true', help='Disable privacy-preserving mining')
    parser.add_argument('--setup-only', action='store_true', help='Setup only, don\'t run client')
    parser.add_argument('--test-connection', action='store_true', help='Test server connection only')
    
    args = parser.parse_args()
    
    logger.info("Setting up Federated Learning Client...")
    
    # Step 1: Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Step 2: Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Step 3: Generate gRPC code
    if not generate_grpc_code():
        sys.exit(1)
    
    # Step 4: Create client configuration
    if not create_client_config(
        args.client_id, args.server_address, args.server_port, 
        args.dataset_path, args.threshold, args.epsilon, not args.no_privacy
    ):
        sys.exit(1)
    
    # Step 5: Create connection test script
    create_connection_test_script(args.server_address, args.server_port)
    
    print("\n" + "="*60)
    print("CLIENT SETUP COMPLETE!")
    print("="*60)
    print(f"Client ID: {args.client_id}")
    print(f"Server: {args.server_address}:{args.server_port}")
    if args.dataset_path:
        print(f"Dataset: {args.dataset_path}")
    print(f"Privacy: {'Enabled' if not args.no_privacy else 'Disabled'}")
    
    if args.test_connection:
        print("\nTesting server connection...")
        if test_server_connection(args.server_address, args.server_port):
            print("✓ Connection test passed!")
        else:
            print("✗ Connection test failed!")
            sys.exit(1)
    
    if not args.setup_only:
        print("\nStarting client... (Press Ctrl+C to stop)")
        success = run_client(
            args.client_id, args.server_address, args.server_port,
            args.dataset_path, args.threshold, args.epsilon, not args.no_privacy
        )
        if not success:
            sys.exit(1)
    else:
        print("\nSetup complete. Run the following to start the client:")
        print(f"python setup_client.py --client-id {args.client_id} --server-address {args.server_address}")
        if args.dataset_path:
            print(f"  --dataset-path {args.dataset_path}")
        if args.no_privacy:
            print("  --no-privacy")
        
        print("\nOr test connection with:")
        print("python test_connection.py")

if __name__ == '__main__':
    main() 