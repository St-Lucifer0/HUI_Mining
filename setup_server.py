#!/usr/bin/env python3
"""
Server setup script for federated learning system
Run this on the laptop that will act as the server
"""

import os
import sys
import subprocess
import argparse
import logging
import socket
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_local_ip():
    """Get the local IP address of this machine"""
    try:
        # Connect to a remote address to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception:
        return "localhost"

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

def create_server_config(host="0.0.0.0", port=50051, threshold=50, epsilon=1.0, rounds=3):
    """Create server configuration file"""
    logger.info("Creating server configuration...")
    
    config = {
        "host": host,
        "port": port,
        "min_utility_threshold": threshold,
        "epsilon": epsilon,
        "num_rounds": rounds,
        "max_clients": 10,
        "timeout_seconds": 300
    }
    
    import json
    with open("server_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    logger.info("Server configuration created")
    return True

def start_server(host="0.0.0.0", port=50051, threshold=50, epsilon=1.0, rounds=3):
    """Start the federated learning server"""
    logger.info(f"Starting federated learning server on {host}:{port}")
    
    try:
        from federated_server import serve
        serve(
            host=host,
            port=port,
            min_utility_threshold=threshold,
            epsilon=epsilon,
            num_rounds=rounds
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return True
    except Exception as e:
        logger.error(f"Server error: {e}")
        return False

def create_client_instructions():
    """Create instructions for client setup"""
    local_ip = get_local_ip()
    
    instructions = f"""
# Client Setup Instructions
# ========================

Server IP Address: {local_ip}
Server Port: 50051

## For Laptop 2 (Client 1):
1. Copy all files to Laptop 2
2. Run: python setup_client.py --client-id client-1 --server-address {local_ip}
3. If you have a dataset: python setup_client.py --client-id client-1 --server-address {local_ip} --dataset-path /path/to/your/dataset.csv

## For Laptop 3 (Client 2):
1. Copy all files to Laptop 3
2. Run: python setup_client.py --client-id client-2 --server-address {local_ip}
3. If you have a dataset: python setup_client.py --client-id client-2 --server-address {local_ip} --dataset-path /path/to/your/dataset.csv

## Network Requirements:
- All laptops must be on the same network
- Firewall must allow connections on port 50051
- Server IP: {local_ip}

## Testing Connection:
From any client laptop, run:
python -c "import grpc; channel = grpc.insecure_channel('{local_ip}:50051'); print('Connection successful')"
"""
    
    with open("CLIENT_SETUP_INSTRUCTIONS.txt", "w") as f:
        f.write(instructions)
    
    logger.info("Client setup instructions created in CLIENT_SETUP_INSTRUCTIONS.txt")
    return instructions

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Setup Federated Learning Server')
    parser.add_argument('--host', default='0.0.0.0', help='Server host (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=50051, help='Server port (default: 50051)')
    parser.add_argument('--threshold', type=float, default=50, help='Utility threshold (default: 50)')
    parser.add_argument('--epsilon', type=float, default=1.0, help='Privacy budget (default: 1.0)')
    parser.add_argument('--rounds', type=int, default=3, help='Number of rounds (default: 3)')
    parser.add_argument('--setup-only', action='store_true', help='Setup only, don\'t start server')
    
    args = parser.parse_args()
    
    logger.info("Setting up Federated Learning Server...")
    
    # Step 1: Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Step 2: Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Step 3: Generate gRPC code
    if not generate_grpc_code():
        sys.exit(1)
    
    # Step 4: Create server configuration
    if not create_server_config(args.host, args.port, args.threshold, args.epsilon, args.rounds):
        sys.exit(1)
    
    # Step 5: Create client instructions
    instructions = create_client_instructions()
    print("\n" + "="*60)
    print("SERVER SETUP COMPLETE!")
    print("="*60)
    print(f"Server will run on: {get_local_ip()}:{args.port}")
    print("\nClient setup instructions have been saved to CLIENT_SETUP_INSTRUCTIONS.txt")
    print("\nInstructions for clients:")
    print(instructions)
    
    if not args.setup_only:
        print("\nStarting server... (Press Ctrl+C to stop)")
        start_server(args.host, args.port, args.threshold, args.epsilon, args.rounds)
    else:
        print("\nSetup complete. Run 'python setup_server.py' to start the server.")

if __name__ == '__main__':
    main() 