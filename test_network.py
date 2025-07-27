#!/usr/bin/env python3
"""
Network connectivity test for federated system
"""

import socket
import subprocess
import sys

def test_ping(server_ip):
    """Test ping connectivity to server"""
    print(f"Testing ping to {server_ip}...")
    try:
        if sys.platform.startswith('win'):
            result = subprocess.run(['ping', '-n', '2', server_ip], 
                                  capture_output=True, text=True, timeout=10)
        else:
            result = subprocess.run(['ping', '-c', '2', server_ip], 
                                  capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"[OK] Ping to {server_ip}: SUCCESS")
            return True
        else:
            print(f"[ERROR] Ping to {server_ip}: FAILED")
            print(f"Output: {result.stdout}")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] Ping test failed: {e}")
        return False

def test_port_connectivity(server_ip, port):
    """Test if a specific port is reachable on the server"""
    print(f"Testing connection to {server_ip}:{port}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((server_ip, port))
        sock.close()
        
        if result == 0:
            print(f"[OK] Port {port} on {server_ip}: REACHABLE")
            return True
        else:
            print(f"[ERROR] Port {port} on {server_ip}: NOT REACHABLE")
            return False
    except Exception as e:
        print(f"[ERROR] Port test failed: {e}")
        return False

def get_local_ip():
    """Get local IP address"""
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"Your local IP: {local_ip}")
        return local_ip
    except Exception as e:
        print(f"[ERROR] Could not get local IP: {e}")
        return None

def main():
    print("NETWORK CONNECTIVITY TEST")
    print("=" * 40)
    
    # Get local IP
    local_ip = get_local_ip()
    
    # Ask for server IP
    server_ip = input("\nEnter the server IP address to test: ").strip()
    
    if not server_ip:
        print("No server IP provided. Exiting.")
        return
    
    print(f"\nTesting connectivity to server: {server_ip}")
    print("-" * 40)
    
    # Test ping
    ping_success = test_ping(server_ip)
    
    # Test ports
    api_port_success = test_port_connectivity(server_ip, 5000)
    federated_port_success = test_port_connectivity(server_ip, 50051)
    
    print("\n" + "=" * 40)
    print("NETWORK TEST SUMMARY")
    print("=" * 40)
    print(f"Ping to {server_ip}: {'SUCCESS' if ping_success else 'FAILED'}")
    print(f"API Port 5000: {'REACHABLE' if api_port_success else 'NOT REACHABLE'}")
    print(f"Federated Port 50051: {'REACHABLE' if federated_port_success else 'NOT REACHABLE'}")
    
    if ping_success and api_port_success and federated_port_success:
        print("\n[OK] All network tests PASSED! You can connect to the server.")
    else:
        print("\n[ERROR] Some network tests FAILED. Check:")
        if not ping_success:
            print("- Network connectivity (firewall, same network)")
        if not api_port_success:
            print("- API server is running on port 5000")
        if not federated_port_success:
            print("- Federated server is running on port 50051")

if __name__ == '__main__':
    main()
