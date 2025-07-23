# 🌐 Network Setup Guide for Multi-Laptop FP-Growth Federated Learning

## Overview

This guide explains how to set up a multi-laptop federated learning system where one laptop acts as a server and other laptops connect as clients to run their datasets collaboratively.

## 🖥️ Server Setup (Laptop 1)

### 1. **Network Configuration**

#### Find Your IP Address
```bash
# Windows
ipconfig

# Look for your local IP address (usually 192.168.x.x or 10.x.x.x)
# Example: IPv4 Address. . . . . . . . . . . : 192.168.1.100
```

#### Configure Firewall
1. **Windows Firewall:**
   - Open Windows Defender Firewall
   - Click "Allow an app or feature through Windows Defender Firewall"
   - Add Python and allow it on both Private and Public networks
   - Or temporarily disable firewall for testing

2. **Port Configuration:**
   - **API Server:** Port 5000 (HTTP)
   - **Federated Server:** Port 50051 (gRPC)
   - **WebSocket:** Port 5000 (same as API)

### 2. **Start the Server**

#### Option A: Using Batch File (Recommended)
```bash
# Run the integrated server batch file
start_integrated_server.bat
```

#### Option B: Manual Start
```bash
# Start the integrated system in server mode
python integrated_system.py --mode server --host 0.0.0.0 --api-port 5000 --federated-port 50051
```

### 3. **Verify Server is Running**

#### Check API Server
```bash
# Test API health endpoint
curl http://localhost:5000/api/health

# Expected response:
{
  "status": "healthy",
  "mode": "server",
  "timestamp": "2024-01-01T12:00:00",
  "federated_server": true
}
```

#### Check Federated Server
```bash
# Test gRPC server (if you have grpcurl installed)
grpcurl -plaintext localhost:50051 list

# Or use the test script
python test_federated_system.py --server-only
```

### 4. **Server Status Indicators**

When the server is running correctly, you should see:
- ✅ Flask API server running on port 5000
- ✅ Federated learning server running on port 50051
- ✅ Web interface accessible at `http://localhost:5000`
- ✅ Browser automatically opens to the dashboard

## 💻 Client Setup (Laptops 2, 3, 4...)

### 1. **Network Connectivity**

#### Test Connection to Server
```bash
# Test if you can reach the server
ping 192.168.1.100  # Replace with server's IP address

# Test API connectivity
curl http://192.168.1.100:5000/api/health

# Test gRPC connectivity (if grpcurl is available)
grpcurl -plaintext 192.168.1.100:50051 list
```

#### Network Requirements
- **Same Network:** All laptops must be on the same WiFi/LAN network
- **No VPN:** Disable VPN connections that might block local traffic
- **Firewall:** Allow Python through firewall on client laptops

### 2. **Prepare Client Data**

#### Option A: Use Sample Data
```bash
# Generate sample dataset for this client
python generate_dataset.py --client-id client-4 --output client4_dataset.csv
```

#### Option B: Use Your Own Data
1. Prepare your CSV file with the following format:
   ```csv
   transaction_id,item1,item2,item3,utility1,utility2,utility3
   1,laptop,mouse,keyboard,800,50,100
   2,phone,charger,case,600,30,20
   ```

2. Place your CSV file in the project directory

### 3. **Start the Client**

#### Option A: Using Batch File (Recommended)
```bash
# Run the integrated client batch file
start_integrated_client.bat
```

#### Option B: Manual Start
```bash
# Start the integrated system in client mode
python integrated_system.py --mode client --client-id client-4 --server-address 192.168.1.100 --federated-port 50051
```

### 4. **Client Configuration**

#### Client ID Convention
- **client-1:** Electronics Store (Server)
- **client-2:** Fashion Store
- **client-3:** Home & Garden Store
- **client-4:** Your Store
- **client-5:** Another Store
- etc.

#### Dataset Assignment
Each client should have a unique dataset:
- **client-4:** `client4_dataset.csv`
- **client-5:** `client5_dataset.csv`
- etc.

## 🔧 Advanced Network Configuration

### 1. **Static IP Setup (Recommended)**

#### On Server Laptop
```bash
# Windows - Set static IP
# Control Panel > Network and Internet > Network Connections
# Right-click WiFi > Properties > Internet Protocol Version 4 > Properties
# Use the following IP address: 192.168.1.100
# Subnet mask: 255.255.255.0
# Default gateway: 192.168.1.1
```

#### On Client Laptops
```bash
# Set static IPs for clients
# Client 2: 192.168.1.101
# Client 3: 192.168.1.102
# Client 4: 192.168.1.103
# etc.
```

### 2. **Port Forwarding (If Needed)**

If laptops are on different networks:
```bash
# On router, forward ports to server laptop
# Port 5000 -> 192.168.1.100:5000
# Port 50051 -> 192.168.1.100:50051
```

### 3. **DNS Resolution**

#### Create Hosts File Entries
```bash
# On each laptop, edit C:\Windows\System32\drivers\etc\hosts
# Add: 192.168.1.100 federated-server
```

## 🧪 Testing the Multi-Laptop Setup

### 1. **Server Dashboard Test**

1. Open browser on server laptop: `http://localhost:5000`
2. Switch to "Server View"
3. Check "Federation Dashboard"
4. You should see connected clients

### 2. **Client Connection Test**

#### Test Script
```bash
# Run on server laptop
python test_federated_system.py --test-connections
```

#### Manual Test
1. Start server on laptop 1
2. Start client on laptop 2
3. Check server dashboard for client connection
4. Repeat for additional clients

### 3. **Federated Learning Test**

#### Start Mining on All Clients
1. On each client laptop, open browser to `http://192.168.1.100:5000`
2. Switch to "Client View"
3. Go to "Mining Controls" tab
4. Click "Start Mining"

#### Monitor Progress
1. On server laptop, check "Server View"
2. Monitor federation status
3. Check global patterns discovery

## 🚨 Troubleshooting

### Common Issues

#### 1. **Connection Refused**
```bash
# Problem: Cannot connect to server
# Solution: Check firewall settings and server IP address
```

#### 2. **Port Already in Use**
```bash
# Problem: Port 5000 or 50051 already in use
# Solution: Kill existing processes or change ports
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

#### 3. **Client Not Appearing in Dashboard**
```bash
# Problem: Client connected but not visible
# Solution: Check client registration and network connectivity
```

#### 4. **Mining Not Starting**
```bash
# Problem: Mining jobs not starting
# Solution: Check dataset files and permissions
```

### Debug Commands

#### Network Debugging
```bash
# Test network connectivity
ping 192.168.1.100
telnet 192.168.1.100 5000
telnet 192.168.1.100 50051

# Check open ports
netstat -an | findstr :5000
netstat -an | findstr :50051
```

#### Application Debugging
```bash
# Check server logs
tail -f integrated_system.log

# Test API endpoints
curl -v http://192.168.1.100:5000/api/health

# Test gRPC endpoints
grpcurl -plaintext 192.168.1.100:50051 list
```

## 📊 Performance Optimization

### 1. **Network Optimization**

#### Bandwidth Considerations
- **Dataset Size:** Keep individual datasets under 100MB
- **Compression:** Enable gzip compression for API responses
- **Batch Processing:** Process data in batches to reduce network overhead

#### Latency Optimization
- **Local Network:** Use wired connections when possible
- **Server Location:** Place server laptop centrally
- **Client Distribution:** Distribute clients evenly across network

### 2. **Resource Management**

#### Server Resources
- **CPU:** Minimum 4 cores recommended
- **RAM:** Minimum 8GB recommended
- **Storage:** SSD preferred for faster I/O

#### Client Resources
- **CPU:** Minimum 2 cores per client
- **RAM:** Minimum 4GB per client
- **Network:** Stable WiFi or wired connection

## 🔒 Security Considerations

### 1. **Network Security**

#### Local Network Security
- **WiFi Password:** Use strong WiFi password
- **Network Isolation:** Consider separate network for federated learning
- **Firewall Rules:** Restrict access to necessary ports only

#### Data Security
- **Encryption:** All communication is encrypted via gRPC
- **Privacy:** Client data never leaves the local machine
- **Authentication:** Consider adding authentication for production use

### 2. **Production Deployment**

#### Additional Security Measures
```bash
# SSL/TLS certificates for HTTPS
# API key authentication
# Rate limiting
# Input validation
# Log monitoring
```

## 📈 Monitoring and Logging

### 1. **Server Monitoring**

#### Log Files
- `integrated_system.log` - Main application logs
- `federated_server.log` - Federated learning logs
- `api_server.log` - API server logs

#### Dashboard Metrics
- Connected clients count
- Federation round progress
- Mining job status
- Network latency

### 2. **Client Monitoring**

#### Health Checks
- Regular heartbeat to server
- Connection status monitoring
- Local resource usage

#### Performance Metrics
- Mining execution time
- Data processing speed
- Network upload/download speeds

## 🎯 Best Practices

### 1. **Network Setup**
- Use static IP addresses for stability
- Test connectivity before starting federated learning
- Monitor network performance during operation

### 2. **Data Management**
- Keep datasets reasonably sized
- Use consistent data formats
- Backup important datasets

### 3. **System Administration**
- Regular system updates
- Monitor disk space and memory usage
- Keep logs for troubleshooting

### 4. **User Training**
- Train users on basic troubleshooting
- Document common procedures
- Provide clear error messages

---

## 🚀 Quick Start Checklist

### Server Setup (Laptop 1)
- [ ] Find server IP address
- [ ] Configure firewall
- [ ] Run `start_integrated_server.bat`
- [ ] Verify server is running
- [ ] Test web interface

### Client Setup (Laptops 2, 3, 4...)
- [ ] Test network connectivity to server
- [ ] Prepare client dataset
- [ ] Run `start_integrated_client.bat`
- [ ] Enter server IP and client ID
- [ ] Verify client connection

### Testing
- [ ] Check server dashboard for clients
- [ ] Start mining on all clients
- [ ] Monitor federation progress
- [ ] Verify global patterns discovery

---

**🎉 Congratulations!** Your multi-laptop federated learning system is now ready for collaborative high-utility itemset mining across multiple datasets. 