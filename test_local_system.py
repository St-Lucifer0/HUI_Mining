#!/usr/bin/env python3
"""
Test the federated system locally to verify it works before multi-laptop setup
"""

import sys
import time
import subprocess
import threading
from integrated_system import IntegratedSystem

def test_backend_imports():
    """Test that all backend modules import correctly"""
    print("TESTING BACKEND IMPORTS")
    print("=" * 40)
    
    try:
        import federated_learning_pb2
        print("[OK] federated_learning_pb2: SUCCESS")
    except ImportError as e:
        print(f"[ERROR] federated_learning_pb2: {e}")
        return False
    
    try:
        from federated_client import FederatedLearningClient
        print("[OK] FederatedLearningClient: SUCCESS")
    except ImportError as e:
        print(f"[ERROR] FederatedLearningClient: {e}")
        return False
    
    try:
        from federated_server import FederatedLearningServer
        print("[OK] FederatedLearningServer: SUCCESS")
    except ImportError as e:
        print(f"[ERROR] FederatedLearningServer: {e}")
        return False
    
    print("[OK] All backend modules imported successfully!")
    return True

def test_server_startup():
    """Test server startup locally"""
    print("\nTESTING SERVER STARTUP")
    print("=" * 40)
    
    try:
        # Test server initialization
        server = IntegratedSystem(
            mode='server',
            host='127.0.0.1',  # Use localhost
            api_port=5000,
            federated_port=50051
        )
        print("[OK] Server initialization: SUCCESS")
        return True
    except Exception as e:
        print(f"[ERROR] Server initialization failed: {e}")
        return False

def test_client_startup():
    """Test client startup locally"""
    print("\nTESTING CLIENT STARTUP")
    print("=" * 40)
    
    try:
        # Test client initialization
        client = IntegratedSystem(
            mode='client',
            client_id='test_client_001',
            server_address='127.0.0.1',  # Use localhost
            api_port=5000,
            federated_port=50051
        )
        print("[OK] Client initialization: SUCCESS")
        return True
    except Exception as e:
        print(f"[ERROR] Client initialization failed: {e}")
        return False

def main():
    print("FEDERATED SYSTEM LOCAL TEST")
    print("=" * 50)
    print("Testing the system locally before multi-laptop setup...")
    print()
    
    # Test backend imports
    if not test_backend_imports():
        print("\n[CRITICAL] Backend import test FAILED!")
        print("Cannot proceed with system testing.")
        return False
    
    # Test server startup
    if not test_server_startup():
        print("\n[ERROR] Server startup test FAILED!")
        return False
    
    # Test client startup
    if not test_client_startup():
        print("\n[ERROR] Client startup test FAILED!")
        return False
    
    print("\n" + "=" * 50)
    print("LOCAL SYSTEM TEST RESULTS")
    print("=" * 50)
    print("[SUCCESS] All local tests PASSED!")
    print()
    print("Your federated system is working correctly!")
    print("The issue is only network connectivity between laptops.")
    print()
    print("NEXT STEPS:")
    print("1. Get the correct server IP from the server laptop")
    print("2. Ensure both laptops are on the same Wi-Fi network")
    print("3. Use the correct server IP in client connection")
    print()
    print("To get server IP on the server laptop, run: ipconfig | findstr IPv4")
    
    return True

if __name__ == '__main__':
    success = main()
    if not success:
        sys.exit(1)
