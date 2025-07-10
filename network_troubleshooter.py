#!/usr/bin/env python3
"""
Network Troubleshooting Script for Federated Learning System
Helps diagnose connectivity issues between clients and server
"""

import socket
import subprocess
import sys
import time
import logging
from typing import Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_local_ip() -> str:
    """Get the local IP address"""
    try:
        # Connect to a remote address to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception:
        return "127.0.0.1"

def test_ping(host: str, port: int = 50051) -> bool:
    """Test if a host is reachable"""
    try:
        # Try to connect to the port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            result = s.connect_ex((host, port))
            return result == 0
    except Exception as e:
        logger.error(f"Ping test failed for {host}:{port}: {e}")
        return False

def test_grpc_connection(host: str, port: int = 50051) -> bool:
    """Test gRPC connection to server"""
    try:
        import grpc
        import federated_learning_pb2
        import federated_learning_pb2_grpc
        
        channel = grpc.insecure_channel(f"{host}:{port}")
        stub = federated_learning_pb2_grpc.FederatedLearningServiceStub(channel)
        
        # Health check
        request = federated_learning_pb2.HealthRequest(client_id="troubleshooter")
        response = stub.HealthCheck(request, timeout=10)
        
        return response.healthy
    except ImportError as e:
        logger.error(f"gRPC modules not available: {e}")
        return False
    except Exception as e:
        logger.error(f"gRPC connection test failed: {e}")
        return False

def check_firewall_windows() -> bool:
    """Check Windows firewall settings"""
    try:
        # Check if port 50051 is allowed
        result = subprocess.run([
            "netsh", "advfirewall", "firewall", "show", "rule", "name=all"
        ], capture_output=True, text=True)
        
        if "50051" in result.stdout:
            logger.info("Port 50051 found in firewall rules")
            return True
        else:
            logger.warning("Port 50051 not found in firewall rules")
            return False
    except Exception as e:
        logger.error(f"Firewall check failed: {e}")
        return False

def add_firewall_rule_windows(port: int = 50051) -> bool:
    """Add Windows firewall rule for the port"""
    try:
        subprocess.run([
            "netsh", "advfirewall", "firewall", "add", "rule",
            f"name=FederatedLearning_{port}",
            "dir=in", "action=allow", "protocol=TCP", f"localport={port}"
        ], check=True)
        
        subprocess.run([
            "netsh", "advfirewall", "firewall", "add", "rule",
            f"name=FederatedLearning_{port}_out",
            "dir=out", "action=allow", "protocol=TCP", f"localport={port}"
        ], check=True)
        
        logger.info(f"Firewall rules added for port {port}")
        return True
    except Exception as e:
        logger.error(f"Failed to add firewall rules: {e}")
        return False

def run_network_diagnostics(server_ip: str, server_port: int = 50051) -> dict:
    """Run comprehensive network diagnostics"""
    results = {
        "local_ip": get_local_ip(),
        "server_ip": server_ip,
        "server_port": server_port,
        "ping_test": False,
        "grpc_test": False,
        "firewall_check": False,
        "recommendations": []
    }
    
    logger.info("="*60)
    logger.info("NETWORK DIAGNOSTICS")
    logger.info("="*60)
    logger.info(f"Local IP: {results['local_ip']}")
    logger.info(f"Server IP: {server_ip}")
    logger.info(f"Server Port: {server_port}")
    
    # Test 1: Basic connectivity
    logger.info("\n1. Testing basic connectivity...")
    results["ping_test"] = test_ping(server_ip, server_port)
    if results["ping_test"]:
        logger.info("✓ Basic connectivity: PASSED")
    else:
        logger.error("✗ Basic connectivity: FAILED")
        results["recommendations"].append("Check if server is running")
        results["recommendations"].append("Verify server IP address")
        results["recommendations"].append("Check network connection")
    
    # Test 2: gRPC connection
    logger.info("\n2. Testing gRPC connection...")
    results["grpc_test"] = test_grpc_connection(server_ip, server_port)
    if results["grpc_test"]:
        logger.info("✓ gRPC connection: PASSED")
    else:
        logger.error("✗ gRPC connection: FAILED")
        results["recommendations"].append("Check if gRPC server is running")
        results["recommendations"].append("Verify server port")
        results["recommendations"].append("Check firewall settings")
    
    # Test 3: Firewall check
    logger.info("\n3. Checking firewall settings...")
    results["firewall_check"] = check_firewall_windows()
    if results["firewall_check"]:
        logger.info("✓ Firewall check: PASSED")
    else:
        logger.warning("⚠ Firewall check: FAILED")
        results["recommendations"].append("Add firewall rule for port 50051")
    
    return results

def print_recommendations(results: dict):
    """Print recommendations based on diagnostic results"""
    logger.info("\n" + "="*60)
    logger.info("RECOMMENDATIONS")
    logger.info("="*60)
    
    if not results["recommendations"]:
        logger.info("✓ All tests passed! Network connectivity looks good.")
        return
    
    for i, rec in enumerate(results["recommendations"], 1):
        logger.info(f"{i}. {rec}")
    
    # Specific actions
    if not results["ping_test"]:
        logger.info("\nIMMEDIATE ACTIONS:")
        logger.info("1. Start the server: python setup_server.py")
        logger.info("2. Verify server IP address is correct")
        logger.info("3. Ensure all devices are on the same network")
    
    if not results["grpc_test"] and results["ping_test"]:
        logger.info("\nIMMEDIATE ACTIONS:")
        logger.info("1. Check if gRPC server is running on the server")
        logger.info("2. Verify server port 50051 is open")
        logger.info("3. Check firewall settings")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python network_troubleshooter.py <server_ip> [port]")
        print("Example: python network_troubleshooter.py 172.20.10.14 50051")
        sys.exit(1)
    
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2]) if len(sys.argv) > 2 else 50051
    
    # Run diagnostics
    results = run_network_diagnostics(server_ip, server_port)
    
    # Print recommendations
    print_recommendations(results)
    
    # Ask if user wants to add firewall rules
    if not results["firewall_check"]:
        print("\n" + "="*60)
        response = input("Would you like to add Windows firewall rules for port 50051? (y/n): ")
        if response.lower() == 'y':
            if add_firewall_rule_windows(server_port):
                print("✓ Firewall rules added successfully!")
                print("Please run the diagnostics again to verify.")
            else:
                print("✗ Failed to add firewall rules. Please add them manually.")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Local IP: {results['local_ip']}")
    print(f"Server IP: {results['server_ip']}")
    print(f"Basic Connectivity: {'✓' if results['ping_test'] else '✗'}")
    print(f"gRPC Connection: {'✓' if results['grpc_test'] else '✗'}")
    print(f"Firewall Check: {'✓' if results['firewall_check'] else '✗'}")
    
    if results["ping_test"] and results["grpc_test"]:
        print("\n🎉 All tests passed! Your network is ready for federated learning.")
    else:
        print("\n⚠ Some tests failed. Please follow the recommendations above.")

if __name__ == "__main__":
    main() 