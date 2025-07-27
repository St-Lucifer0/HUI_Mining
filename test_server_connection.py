#!/usr/bin/env python3
"""
Test connectivity to the federated server
"""

import socket
import subprocess
import sys

def test_server_connectivity(server_ip):
    """Test connectivity to the server"""
    print(f"TESTING CONNECTIVITY TO SERVER: {server_ip}")
    print("=" * 50)
    
    # Test ping
    print(f"1. Testing ping to {server_ip}...")
    try:
        result = subprocess.run(['ping', '-n', '2', server_ip], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("[OK] Ping: SUCCESS - Server is reachable!")
        else:
            print("[ERROR] Ping: FAILED - Server not reachable")
            print("Check that both laptops are on the same network")
            return False
    except Exception as e:
        print(f"[ERROR] Ping test failed: {e}")
        return False
    
    # Test API port (5000)
    print(f"2. Testing API port 5000...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((server_ip, 5000))
        sock.close()
        
        if result == 0:
            print("[OK] API Port 5000: REACHABLE - Server is running!")
        else:
            print("[WARNING] API Port 5000: NOT REACHABLE")
            print("Make sure the server is running: start_integrated_server.bat")
    except Exception as e:
        print(f"[ERROR] API port test failed: {e}")
    
    # Test federated port (50051)
    print(f"3. Testing federated port 50051...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((server_ip, 50051))
        sock.close()
        
        if result == 0:
            print("[OK] Federated Port 50051: REACHABLE - Server is running!")
        else:
            print("[WARNING] Federated Port 50051: NOT REACHABLE")
            print("Make sure the server is running: start_integrated_server.bat")
    except Exception as e:
        print(f"[ERROR] Federated port test failed: {e}")
    
    return True

def main():
    print("FEDERATED SERVER CONNECTIVITY TEST")
    print("=" * 50)
    
    # Get server IP from user
    server_ip = input("Enter the server IP address: ").strip()
    
    if not server_ip:
        print("No server IP provided. Exiting.")
        return
    
    print(f"\nYour current IP: 192.168.137.160")
    print(f"Testing server IP: {server_ip}")
    print()
    
    # Test connectivity
    success = test_server_connectivity(server_ip)
    
    print("\n" + "=" * 50)
    if success:
        print("CONNECTIVITY TEST COMPLETE")
        print("\nIf ping succeeded but ports are not reachable:")
        print("1. Start the server: start_integrated_server.bat")
        print("2. Then start the client: start_integrated_client.bat")
    else:
        print("CONNECTIVITY TEST FAILED")
        print("\nTo fix:")
        print("1. Ensure both laptops are on the same Wi-Fi network")
        print("2. Get the correct server IP: ipconfig | findstr IPv4")
        print("3. Use that IP address instead")

if __name__ == '__main__':
    main()
