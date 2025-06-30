# Quick Start Guide: 3-Laptop Federated Learning

## 🚀 **Super Quick Setup (5 minutes)**

### **Step 1: Copy Files**
- Copy the entire project folder to all 3 laptops
- Ensure all laptops are on the same WiFi network

### **Step 2: Start Server (Laptop 1)**
```bash
# Windows
start_server.bat

# Or manually:
python setup_server.py
```
**Note the IP address** that appears (e.g., `192.168.1.100`)

### **Step 3: Start Client 1 (Laptop 2)**
```bash
# Windows
start_client.bat
# Enter: client-1, SERVER_IP, dataset path (optional)

# Or manually:
python setup_client.py --client-id client-1 --server-address SERVER_IP
```

### **Step 4: Start Client 2 (Laptop 3)**
```bash
# Windows
start_client.bat
# Enter: client-2, SERVER_IP, dataset path (optional)

# Or manually:
python setup_client.py --client-id client-2 --server-address SERVER_IP
```

## 📋 **What Each Laptop Does**

| Laptop | Role | What It Does |
|--------|------|--------------|
| **Laptop 1** | Server | Aggregates results from clients |
| **Laptop 2** | Client 1 | Runs FP-Growth on local data |
| **Laptop 3** | Client 2 | Runs FP-Growth on local data |

## 🔧 **Troubleshooting**

### **"Connection refused"**
- Check if server is running on Laptop 1
- Verify server IP address
- Check Windows Firewall

### **"No route to host"**
- Ensure all laptops are on same WiFi
- Try `ping SERVER_IP` from clients

### **"Module not found"**
- Run: `pip install -r requirements.txt`
- Run: `python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. federated_learning.proto`

## 📊 **Expected Output**

### **Server (Laptop 1)**
```
Federated Learning Server started on 192.168.1.100:50051
Client client-1 registered successfully
Client client-2 registered successfully
Results received from client-1: 15 itemsets
Results received from client-2: 12 itemsets
Global aggregation completed
```

### **Clients (Laptops 2 & 3)**
```
Connected to server successfully
Local mining completed: 15 high-utility itemsets
Results sent to server
Global results received: 25 aggregated itemsets
```

## 🎯 **Success!**

When you see:
- ✅ All laptops connected
- ✅ Local mining completed
- ✅ Global results aggregated
- ✅ No error messages

**Your federated learning system is working!**

## 📞 **Need Help?**

1. Check `network_setup_guide.md` for detailed instructions
2. Run `python test_connection.py` to test connectivity
3. Check logs for specific error messages
4. Ensure all laptops have Python 3.9+ installed

## 🔄 **Next Steps**

- Use real datasets instead of sample data
- Adjust privacy parameters (epsilon values)
- Add more clients
- Monitor performance metrics 