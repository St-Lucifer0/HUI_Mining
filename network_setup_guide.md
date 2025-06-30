# Network Setup Guide for 3-Laptop Federated Learning

This guide will help you set up your three laptops for federated learning.

## 📋 Prerequisites

- All three laptops must have Python 3.9+ installed
- All laptops must be on the same network (WiFi or Ethernet)
- Firewall settings must allow connections on port 50051

## 🖥️ Laptop Configuration

### **Laptop 1 (Server)**
- **Role**: Federated Learning Server
- **IP**: Will be determined automatically
- **Port**: 50051

### **Laptop 2 (Client 1)**
- **Role**: Federated Learning Client
- **Client ID**: client-1
- **Connects to**: Laptop 1

### **Laptop 3 (Client 2)**
- **Role**: Federated Learning Client
- **Client ID**: client-2
- **Connects to**: Laptop 1

## 🔧 Step-by-Step Setup

### **Step 1: Prepare All Laptops**

1. **Copy the entire project folder** to all three laptops
2. **Ensure all laptops are on the same network**
3. **Check network connectivity** between laptops

### **Step 2: Setup Server (Laptop 1)**

1. **Open Command Prompt/Terminal** on Laptop 1
2. **Navigate to the project folder**
3. **Run the server setup**:

```bash
# Setup and start server
python setup_server.py

# Or setup only (then start manually)
python setup_server.py --setup-only
```

4. **Note the server IP address** that appears in the output
5. **Keep the server running** (don't close the terminal)

### **Step 3: Setup Client 1 (Laptop 2)**

1. **Open Command Prompt/Terminal** on Laptop 2
2. **Navigate to the project folder**
3. **Run the client setup**:

```bash
# Replace SERVER_IP with the IP from Laptop 1
python setup_client.py --client-id client-1 --server-address SERVER_IP

# If you have a dataset:
python setup_client.py --client-id client-1 --server-address SERVER_IP --dataset-path /path/to/dataset.csv
```

### **Step 4: Setup Client 2 (Laptop 3)**

1. **Open Command Prompt/Terminal** on Laptop 3
2. **Navigate to the project folder**
3. **Run the client setup**:

```bash
# Replace SERVER_IP with the IP from Laptop 1
python setup_client.py --client-id client-2 --server-address SERVER_IP

# If you have a dataset:
python setup_client.py --client-id client-2 --server-address SERVER_IP --dataset-path /path/to/dataset.csv
```

## 🌐 Network Troubleshooting

### **Finding Server IP Address**

On Laptop 1 (Server), run:
```bash
# Windows
ipconfig

# Look for IPv4 Address under your network adapter
# Example: 192.168.1.100
```

### **Testing Network Connectivity**

From any client laptop, test connection:
```bash
# Test basic connectivity
ping SERVER_IP

# Test specific port
telnet SERVER_IP 50051
```

### **Firewall Configuration**

#### **Windows Firewall**
1. Open Windows Defender Firewall
2. Click "Allow an app or feature through Windows Defender Firewall"
3. Click "Change settings"
4. Click "Allow another app"
5. Browse to your Python executable
6. Make sure both Private and Public are checked

#### **Alternative: Allow Port 50051**
```bash
# Run as Administrator
netsh advfirewall firewall add rule name="Federated Learning" dir=in action=allow protocol=TCP localport=50051
```

### **Common Network Issues**

1. **"Connection refused"**
   - Check if server is running
   - Verify server IP address
   - Check firewall settings

2. **"No route to host"**
   - Ensure all laptops are on same network
   - Check WiFi/Ethernet connection
   - Try pinging the server IP

3. **"Timeout"**
   - Check firewall settings
   - Verify port 50051 is open
   - Check network congestion

## 🚀 Running the System

### **Start Order**
1. **Start Server first** (Laptop 1)
2. **Start Client 1** (Laptop 2)
3. **Start Client 2** (Laptop 3)

### **Monitoring**

#### **Server Monitoring (Laptop 1)**
```bash
# View server logs
python run_federated_system.py logs federated-server

# Check server status
python run_federated_system.py status
```

#### **Client Monitoring**
Each client will show its own logs in the terminal.

### **Stopping the System**
1. **Stop clients first** (Ctrl+C on client terminals)
2. **Stop server** (Ctrl+C on server terminal)

## 📊 Expected Behavior

### **Server (Laptop 1)**
- Shows "Federated Learning Server started"
- Displays client registrations
- Shows aggregation progress
- Displays final results

### **Clients (Laptops 2 & 3)**
- Connect to server
- Run local FP-Growth mining
- Send results to server
- Receive global aggregated results

## 🔍 Troubleshooting Commands

### **Test Server Connection**
```bash
python test_connection.py
```

### **Check Dependencies**
```bash
python -c "import grpc; print('gRPC OK')"
python -c "import federated_learning_pb2; print('Protobuf OK')"
```

### **Manual Connection Test**
```bash
python -c "import grpc; channel = grpc.insecure_channel('SERVER_IP:50051'); print('Connection successful')"
```

## 📱 Alternative: Using Docker

If you prefer Docker deployment:

### **Server (Laptop 1)**
```bash
docker-compose up federated-server
```

### **Clients (Laptops 2 & 3)**
```bash
# Modify docker-compose.yml to point to server IP
# Then run:
docker-compose up client-1  # or client-2
```

## 🎯 Success Indicators

- Server shows "Client registered successfully"
- Clients show "Connected to server"
- Server shows "Results received from client-X"
- Final output shows aggregated high-utility itemsets
- All laptops complete without errors

## 📞 Getting Help

If you encounter issues:

1. **Check the logs** for error messages
2. **Verify network connectivity**
3. **Test with simple connection first**
4. **Check firewall settings**
5. **Ensure all dependencies are installed**

## 🔄 Next Steps

Once the basic system is working:

1. **Add more clients** by copying the setup to additional laptops
2. **Use real datasets** instead of sample data
3. **Adjust privacy parameters** (epsilon values)
4. **Monitor performance** and optimize settings
5. **Scale the system** for larger datasets 