#!/usr/bin/env python3
"""
Test script for the federated learning system
"""

import time
import subprocess
import sys
import os
import logging
from typing import Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_grpc_generation():
    """Test if gRPC code generation works"""
    logger.info("Testing gRPC code generation...")
    
    try:
        # Check if protobuf file exists
        if not os.path.exists('federated_learning.proto'):
            logger.error("federated_learning.proto not found")
            return False
        
        # Generate gRPC code
        result = subprocess.run([
            'python', '-m', 'grpc_tools.protoc', 
            '-I.', '--python_out=.', '--grpc_python_out=.', 
            'federated_learning.proto'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"gRPC generation failed: {result.stderr}")
            return False
        
        # Check if generated files exist
        required_files = [
            'federated_learning_pb2.py',
            'federated_learning_pb2_grpc.py'
        ]
        
        for file in required_files:
            if not os.path.exists(file):
                logger.error(f"Generated file {file} not found")
                return False
        
        logger.info("gRPC code generation successful")
        return True
        
    except Exception as e:
        logger.error(f"Error testing gRPC generation: {e}")
        return False

def test_imports():
    """Test if all required modules can be imported"""
    logger.info("Testing module imports...")
    
    try:
        # Test gRPC imports
        import federated_learning_pb2
        import federated_learning_pb2_grpc
        logger.info("gRPC modules imported successfully")
        
        # Test federated learning modules
        from federated_server import FederatedLearningServer
        from federated_client import FederatedLearningClient
        logger.info("Federated learning modules imported successfully")
        
        # Test existing FP-Growth modules
        from preprocessor import construct_pruned_item_list
        from fp_tree_builder import construct_huim_fp_tree
        from hui_miner import HUIMiner
        from privacy_wrapper import PrivacyPreservingHUIMining
        from data_parser import DataProcessor
        logger.info("FP-Growth modules imported successfully")
        
        return True
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        return False
    except Exception as e:
        logger.error(f"Error testing imports: {e}")
        return False

def test_server_creation():
    """Test if server can be created"""
    logger.info("Testing server creation...")
    
    try:
        from federated_server import FederatedLearningServer
        
        server = FederatedLearningServer(
            min_utility_threshold=50,
            epsilon=1.0,
            num_rounds=3
        )
        
        # Test server methods
        stats = server.get_server_stats()
        logger.info(f"Server stats: {stats}")
        
        logger.info("Server creation successful")
        return True
        
    except Exception as e:
        logger.error(f"Error testing server creation: {e}")
        return False

def test_client_creation():
    """Test if client can be created"""
    logger.info("Testing client creation...")
    
    try:
        from federated_client import FederatedLearningClient
        
        client = FederatedLearningClient(
            client_id="test-client",
            server_address="localhost",
            server_port=50051,
            min_utility_threshold=50,
            epsilon=1.0
        )
        
        logger.info("Client creation successful")
        return True
        
    except Exception as e:
        logger.error(f"Error testing client creation: {e}")
        return False

def test_local_mining():
    """Test local FP-Growth mining"""
    logger.info("Testing local mining...")
    
    try:
        from federated_client import FederatedLearningClient
        
        client = FederatedLearningClient(
            client_id="test-client",
            server_address="localhost",
            server_port=50051
        )
        
        # Load sample data
        success = client.load_local_data()
        if not success:
            logger.error("Failed to load local data")
            return False
        
        # Run local mining
        success = client.run_local_mining()
        if not success:
            logger.error("Failed to run local mining")
            return False
        
        logger.info(f"Local mining successful: {len(client.local_itemsets)} itemsets found")
        return True
        
    except Exception as e:
        logger.error(f"Error testing local mining: {e}")
        return False

def test_privacy_preserving_mining():
    """Test privacy-preserving mining"""
    logger.info("Testing privacy-preserving mining...")
    
    try:
        from federated_client import FederatedLearningClient
        
        client = FederatedLearningClient(
            client_id="test-client",
            server_address="localhost",
            server_port=50051
        )
        
        # Load sample data
        success = client.load_local_data()
        if not success:
            logger.error("Failed to load local data")
            return False
        
        # Run privacy-preserving mining
        success = client.run_privacy_preserving_mining()
        if not success:
            logger.error("Failed to run privacy-preserving mining")
            return False
        
        logger.info(f"Privacy-preserving mining successful: {len(client.local_itemsets)} itemsets found")
        return True
        
    except Exception as e:
        logger.error(f"Error testing privacy-preserving mining: {e}")
        return False

def test_docker_build():
    """Test Docker image building"""
    logger.info("Testing Docker build...")
    
    try:
        # Test server Dockerfile
        result = subprocess.run([
            'docker', 'build', '-f', 'Dockerfile.server', '-t', 'test-federated-server', '.'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Server Docker build failed: {result.stderr}")
            return False
        
        # Test client Dockerfile
        result = subprocess.run([
            'docker', 'build', '-f', 'Dockerfile.client', '-t', 'test-federated-client', '.'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Client Docker build failed: {result.stderr}")
            return False
        
        logger.info("Docker builds successful")
        return True
        
    except Exception as e:
        logger.error(f"Error testing Docker build: {e}")
        return False

def test_docker_compose():
    """Test Docker Compose configuration"""
    logger.info("Testing Docker Compose...")
    
    try:
        # Validate docker-compose file
        result = subprocess.run([
            'docker-compose', '-f', 'docker-compose.yml', 'config'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Docker Compose validation failed: {result.stderr}")
            return False
        
        logger.info("Docker Compose configuration valid")
        return True
        
    except Exception as e:
        logger.error(f"Error testing Docker Compose: {e}")
        return False

def cleanup_test_images():
    """Clean up test Docker images"""
    logger.info("Cleaning up test images...")
    
    try:
        subprocess.run(['docker', 'rmi', 'test-federated-server'], capture_output=True)
        subprocess.run(['docker', 'rmi', 'test-federated-client'], capture_output=True)
        logger.info("Test images cleaned up")
    except Exception as e:
        logger.warning(f"Error cleaning up test images: {e}")

def run_all_tests():
    """Run all tests"""
    logger.info("Starting federated learning system tests...")
    
    tests = [
        ("gRPC Generation", test_grpc_generation),
        ("Module Imports", test_imports),
        ("Server Creation", test_server_creation),
        ("Client Creation", test_client_creation),
        ("Local Mining", test_local_mining),
        ("Privacy-Preserving Mining", test_privacy_preserving_mining),
        ("Docker Build", test_docker_build),
        ("Docker Compose", test_docker_compose),
    ]
    
    results = {}
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running test: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            success = test_func()
            results[test_name] = success
            if success:
                passed += 1
                logger.info(f"✓ {test_name} PASSED")
            else:
                logger.error(f"✗ {test_name} FAILED")
        except Exception as e:
            results[test_name] = False
            logger.error(f"✗ {test_name} FAILED with exception: {e}")
    
    # Clean up
    cleanup_test_images()
    
    # Print summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    for test_name, success in results.items():
        status = "PASSED" if success else "FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! The federated learning system is ready to use.")
        return True
    else:
        logger.error("❌ Some tests failed. Please check the errors above.")
        return False

def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("""
Federated Learning System Test Suite

Usage:
    python test_federated_system.py          # Run all tests
    python test_federated_system.py --help   # Show this help

Tests included:
1. gRPC Generation - Tests protobuf compilation
2. Module Imports - Tests all required modules
3. Server Creation - Tests federated server
4. Client Creation - Tests federated client
5. Local Mining - Tests FP-Growth mining
6. Privacy-Preserving Mining - Tests privacy features
7. Docker Build - Tests Docker image building
8. Docker Compose - Tests system orchestration
        """)
        return
    
    success = run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main() 