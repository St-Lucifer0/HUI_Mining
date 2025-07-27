#!/usr/bin/env python3
"""
Network Diagnostic Tool for Federated System
Helps identify network connectivity issues between client and server
"""

import socket
import subprocess
import sys
import ipaddress

def get_network_info():
    """Get local network information"""
    print("LOCAL NETWORK INFORMATION")
    print("=" * 40)
    
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"Hostname: {hostname}")
        print(f"Local IP: {local_ip}")
        
        # Determine network subnet
        try:
            network = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
            print(f"Network Subnet: {network}")
        except:
            print("Could not determine network subnet")
            
        return local_ip
    except Exception as e:
        print(f"[ERROR] Could not get network info: {e}")
        return None

def check_same_network(ip1, ip2):
    """Check if two IPs are on the same network"""
    try:
        net1 = ipaddress.IPv4Network(f"{ip1}/24", strict=False)
        net2 = ipaddress.IPv4Network(f"{ip2}/24", strict=False)
        
        if net1.network_address == net2.network_address:
            print(f"[OK] Both IPs are on the same network: {net1}")
            return True
        else:
            print(f"[WARNING] IPs are on different networks:")
            print(f"  Client network: {net1}")
            print(f"  Server network: {net2}")
            return False
    except Exception as e:
        print(f"[ERROR] Could not compare networks: {e}")
        return False

def test_basic_connectivity():
    """Test basic network connectivity"""
    print("\nBASIC CONNECTIVITY TEST")
    print("=" * 40)
    
    # Test internet connectivity
    try:
        result = subprocess.run(['ping', '-n', '1', '8.8.8.8'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("[OK] Internet connectivity: WORKING")
        else:
            print("[WARNING] Internet connectivity: FAILED")
    except:
        print("[WARNING] Could not test internet connectivity")
    
    # Test local network gateway
    try:
        result = subprocess.run(['ipconfig'], capture_output=True, text=True)
        if 'Default Gateway' in result.stdout:
            print("[OK] Network configuration: DETECTED")
        else:
            print("[WARNING] Network configuration: ISSUES DETECTED")
    except:
        print("[WARNING] Could not check network configuration")

def suggest_solutions(local_ip, server_ip):
    """Suggest solutions based on network analysis"""
    print("\nRECOMMENDED SOLUTIONS")
    print("=" * 40)
    
    # Check if on same network
    same_network = check_same_network(local_ip, server_ip)
    
    if not same_network:
        print("\n1. NETWORK CONNECTIVITY ISSUE:")
        print("   - Ensure both laptops are connected to the SAME Wi-Fi network")
        print("   - Check if one is using Wi-Fi and the other Ethernet")
        print("   - If using mobile hotspot, connect both devices to it")
        print("   - Restart your router/network equipment")
    
    print("\n2. FIREWALL SOLUTIONS:")
    print("   - Run 'fix_firewall_complete.bat' as Administrator on BOTH laptops")
    print("   - Temporarily disable Windows Firewall for testing")
    print("   - Check antivirus software firewall settings")
    
    print("\n3. SERVER VERIFICATION:")
    print("   - Ensure the server is actually running on the target IP")
    print("   - Verify the server IP address is correct")
    print("   - Check if server ports 5000 and 50051 are open")
    
    print("\n4. ALTERNATIVE TESTING:")
    print("   - Try using the server's actual IP address from ipconfig")
    print("   - Test with localhost (127.0.0.1) if on same machine")
    print("   - Use network scanning tools to find the server")

def main():
    print("FEDERATED SYSTEM NETWORK DIAGNOSTIC")
    print("=" * 50)
    
    # Get local network info
    local_ip = get_network_info()
    
    # Test basic connectivity
    test_basic_connectivity()
    
    # Get server IP for analysis
    print(f"\nSERVER CONNECTIVITY ANALYSIS")
    print("=" * 40)
    
    # Use the known problematic server IP
    server_ip = "192.168.1.100"
    print(f"Analyzing connectivity to server: {server_ip}")
    
    if local_ip:
        suggest_solutions(local_ip, server_ip)
    
    print(f"\nNETWORK DIAGNOSTIC COMPLETE")
    print("=" * 50)
    print("Follow the recommended solutions above to resolve connectivity issues.")

if __name__ == '__main__':
    main()
