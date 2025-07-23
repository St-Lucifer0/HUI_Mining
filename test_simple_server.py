#!/usr/bin/env python3
"""
Simple server test to isolate import issues
"""

import sys
import time
import requests

def test_basic_imports():
    """Test basic imports without gRPC"""
    print("Testing basic imports...")
    
    try:
        from flask import Flask
        print("✅ Flask import successful")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        from flask_cors import CORS
        print("✅ Flask-CORS import successful")
    except ImportError as e:
        print(f"❌ Flask-CORS import failed: {e}")
        return False
    
    try:
        from flask_socketio import SocketIO
        print("✅ Flask-SocketIO import successful")
    except ImportError as e:
        print(f"❌ Flask-SocketIO import failed: {e}")
        return False
    
    return True

def test_backend_imports():
    """Test backend module imports"""
    print("\nTesting backend imports...")
    
    modules = [
        ('config', 'config'),
        ('data_parser', 'DataProcessor'),
        ('preprocessor', 'construct_pruned_item_list'),
        ('fp_tree_builder', 'construct_huim_fp_tree'),
        ('hui_miner', 'HUIMiner'),
        ('privacy_wrapper', 'PrivacyPreservingHUIMining'),
        ('output_formatter', 'FederatedLearningOutputFormatter'),
        ('performance_monitor', 'PerformanceMonitor'),
    ]
    
    all_success = True
    for module_name, class_name in modules:
        try:
            module = __import__(module_name)
            if hasattr(module, class_name):
                print(f"✅ {module_name}: {class_name} available")
            else:
                print(f"⚠️  {module_name}: {class_name} not found")
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
            all_success = False
    
    return all_success

def test_grpc_imports():
    """Test gRPC imports"""
    print("\nTesting gRPC imports...")
    
    try:
        import grpc
        print("✅ grpc import successful")
    except ImportError as e:
        print(f"❌ grpc import failed: {e}")
        return False
    
    try:
        from federated_learning_pb2 import *
        print("✅ federated_learning_pb2 import successful")
    except ImportError as e:
        print(f"❌ federated_learning_pb2 import failed: {e}")
        return False
    
    try:
        from federated_learning_pb2_grpc import *
        print("✅ federated_learning_pb2_grpc import successful")
    except ImportError as e:
        print(f"❌ federated_learning_pb2_grpc import failed: {e}")
        return False
    
    return True

def test_server_start():
    """Test if server can start"""
    print("\nTesting server start...")
    
    try:
        # Import the integrated system
        from integrated_system import IntegratedSystem
        
        # Create server instance
        server = IntegratedSystem(mode='server', host='127.0.0.1', api_port=5001, federated_port=50052)
        print("✅ IntegratedSystem created successfully")
        
        # Try to start server mode
        server.start_server_mode()
        print("✅ Server started successfully")
        
        # Wait a moment
        time.sleep(2)
        
        # Test health endpoint
        try:
            response = requests.get("http://127.0.0.1:5001/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ Health endpoint responding")
            else:
                print(f"⚠️  Health endpoint returned {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Health endpoint failed: {e}")
        
        # Stop server
        server.stop()
        print("✅ Server stopped successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🔍 Simple Server Test")
    print("=" * 50)
    
    # Test basic imports
    if not test_basic_imports():
        print("\n❌ Basic imports failed. Install required packages.")
        return
    
    # Test backend imports
    backend_ok = test_backend_imports()
    
    # Test gRPC imports
    grpc_ok = test_grpc_imports()
    
    # Test server start
    if backend_ok and grpc_ok:
        test_server_start()
    else:
        print("\n⚠️  Skipping server start due to import issues")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == '__main__':
    main() 