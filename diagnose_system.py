#!/usr/bin/env python3
"""
Comprehensive System Diagnostic Tool
Diagnoses Python version, package compatibility, and network connectivity issues
"""

import sys
import os
import subprocess
import socket
import importlib.util

def print_section(title):
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

def check_python_version():
    print_section("PYTHON VERSION CHECK")
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("[OK] Running in virtual environment")
        print(f"Virtual Environment Path: {sys.prefix}")
    else:
        print("[WARNING] NOT running in virtual environment")
    
    # Check Python version compatibility
    version_info = sys.version_info
    if version_info >= (3, 11):
        print("[OK] Python version is 3.11+ (recommended)")
    elif version_info >= (3, 9):
        print("[WARNING] Python version is 3.9-3.10 (may have compatibility issues)")
    else:
        print("[ERROR] Python version is too old (< 3.9) - UPGRADE REQUIRED")

def check_package_imports():
    print_section("PACKAGE IMPORT CHECK")
    
    packages_to_check = [
        ('grpc', 'grpcio'),
        ('google.protobuf', 'protobuf'),
        ('google.protobuf.runtime_version', 'protobuf runtime_version'),
        ('numpy', 'numpy'),
        ('pandas', 'pandas'),
        ('flask', 'flask'),
        ('cryptography', 'cryptography'),
    ]
    
    for package, display_name in packages_to_check:
        try:
            module = importlib.import_module(package)
            if hasattr(module, '__version__'):
                print(f"[OK] {display_name}: {module.__version__}")
            else:
                print(f"[OK] {display_name}: Available (no version info)")
        except ImportError as e:
            print(f"[ERROR] {display_name}: FAILED - {e}")

def check_protobuf_compatibility():
    print_section("PROTOBUF COMPATIBILITY CHECK")
    
    try:
        import google.protobuf
        print(f"Protobuf version: {google.protobuf.__version__}")
        
        # Try to import runtime_version specifically
        try:
            from google.protobuf import runtime_version
            print("[OK] runtime_version import: SUCCESS")
        except ImportError as e:
            print(f"[ERROR] runtime_version import: FAILED - {e}")
            print("   This indicates protobuf version incompatibility")
        
        # Check if federated_learning_pb2 can be imported
        try:
            import federated_learning_pb2
            print("[OK] federated_learning_pb2 import: SUCCESS")
        except ImportError as e:
            print(f"[ERROR] federated_learning_pb2 import: FAILED - {e}")
            
    except ImportError as e:
        print(f"[ERROR] Protobuf not installed: {e}")

def check_network_connectivity():
    print_section("NETWORK CONNECTIVITY CHECK")
    
    # Get local IP addresses
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
        print(f"Hostname: {hostname}")
        print(f"Local IP: {local_ip}")
    except Exception as e:
        print(f"[ERROR] Could not get local IP: {e}")
    
    # Test if ports are available
    ports_to_check = [5000, 50051]
    
    for port in ports_to_check:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        try:
            result = sock.connect_ex(('localhost', port))
            if result == 0:
                print(f"[WARNING] Port {port}: IN USE (server may be running)")
            else:
                print(f"[OK] Port {port}: AVAILABLE")
        except Exception as e:
            print(f"[ERROR] Port {port}: ERROR - {e}")
        finally:
            sock.close()

def check_project_files():
    print_section("PROJECT FILES CHECK")
    
    required_files = [
        'integrated_system.py',
        'federated_server.py',
        'federated_client.py',
        'federated_learning.proto',
        'federated_learning_pb2.py',
        'federated_learning_pb2_grpc.py',
        'requirements.txt',
        'hui_miner.py',
        'config.py'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"[OK] {file}: EXISTS")
        else:
            print(f"[ERROR] {file}: MISSING")

def test_server_ping(server_ip):
    print_section(f"PING TEST TO {server_ip}")
    
    try:
        # Use ping command
        if os.name == 'nt':  # Windows
            result = subprocess.run(['ping', '-n', '4', server_ip], 
                                  capture_output=True, text=True, timeout=10)
        else:  # Unix/Linux
            result = subprocess.run(['ping', '-c', '4', server_ip], 
                                  capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"[OK] Ping to {server_ip}: SUCCESS")
            print("Network connectivity is working")
        else:
            print(f"[ERROR] Ping to {server_ip}: FAILED")
            print("Network connectivity issues detected")
            print(f"Error output: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print(f"[ERROR] Ping to {server_ip}: TIMEOUT")
    except Exception as e:
        print(f"[ERROR] Ping to {server_ip}: ERROR - {e}")

def main():
    print("FEDERATED SYSTEM DIAGNOSTIC TOOL")
    print("This tool will help identify Python, package, and network issues")
    
    # Run all diagnostic checks
    check_python_version()
    check_package_imports()
    check_protobuf_compatibility()
    check_project_files()
    check_network_connectivity()
    
    # Ask for server IP to test
    print(f"\n{'='*50}")
    server_ip = input("Enter server IP address to test (e.g., 192.168.1.100): ").strip()
    if server_ip:
        test_server_ping(server_ip)
    
    print_section("DIAGNOSTIC COMPLETE")
    print("Review the results above to identify issues.")
    print("\nCommon solutions:")
    print("1. If Python < 3.11: Upgrade Python")
    print("2. If protobuf issues: pip install --upgrade protobuf")
    print("3. If network issues: Check firewall and network settings")
    print("4. If missing files: Ensure complete project copy/clone")

if __name__ == '__main__':
    main()
