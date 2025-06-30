# 🖥️ 3-Laptop Federated Learning Setup Summary

## 📁 **Files You Need to Copy to All 3 Laptops**

### **Core Files (Required)**
```
├── federated_learning.proto          # gRPC service definition
├── federated_server.py               # Server implementation
├── federated_client.py               # Client implementation
├── setup_server.py                   # Server setup script
├── setup_client.py                   # Client setup script
├── requirements.txt                  # Python dependencies
├── start_server.bat                  # Windows server launcher
├── start_client.bat                  # Windows client launcher
├── test_connection.py                # Connection test script
├── network_setup_guide.md            # Detailed network guide
├── QUICK_START_3_LAPTOPS.md          # Quick start guide
└── Your existing FP-Growth files:    # Your original code
    ├── main.py
    ├── hui_miner.py
    ├── privacy_wrapper.py
    ├── data_parser.py
    ├── preprocessor.py
    ├── fp_tree_builder.py
    ├── fp_tree_updater.py
    ├── hui_miner_helpers.py
    ├── fp_node.py
    ├── differential_privacy_utils.py
    ├── dummy_mpc.py
    └── foodmart_dataset_csv.csv
```

## 🚀 **Step-by-Step Instructions**

### **Phase 1: Preparation (5 minutes)**
1. **Copy the entire project folder** to all 3 laptops
2. **Ensure all laptops are on the same WiFi network**
3. **Check that all laptops have Python 3.9+ installed**

### **Phase 2: Server Setup (Laptop 1)**
1. **Open Command Prompt** on Laptop 1
2. **Navigate to project folder**
3. **Run one of these commands**:
   ```bash
   # Option A: Windows batch file (easiest)
   start_server.bat
   
   # Option B: Python script
   python setup_server.py
   
   # Option C: Setup only, then start manually
   python setup_server.py --setup-only
   python setup_server.py
   ```
4. **Note the server IP address** (e.g., `192.168.1.100`)
5. **Keep the server running** (don't close the terminal)

### **Phase 3: Client 1 Setup (Laptop 2)**
1. **Open Command Prompt** on Laptop 2
2. **Navigate to project folder**
3. **Run one of these commands**:
   ```bash
   # Option A: Windows batch file (interactive)
   start_client.bat
   # Enter: client-1, SERVER_IP, dataset path (optional)
   
   # Option B: Python script (direct)
   python setup_client.py --client-id client-1 --server-address SERVER_IP
   
   # Option C: With dataset
   python setup_client.py --client-id client-1 --server-address SERVER_IP --dataset-path foodmart_dataset_csv.csv
   ```

### **Phase 4: Client 2 Setup (Laptop 3)**
1. **Open Command Prompt** on Laptop 3
2. **Navigate to project folder**
3. **Run one of these commands**:
   ```bash
   # Option A: Windows batch file (interactive)
   start_client.bat
   # Enter: client-2, SERVER_IP, dataset path (optional)
   
   # Option B: Python script (direct)
   python setup_client.py --client-id client-2 --server-address SERVER_IP
   
   # Option C: With dataset
   python setup_client.py --client-id client-2 --server-address SERVER_IP --dataset-path foodmart_dataset_csv.csv
   ```

## 🔧 **Troubleshooting Quick Reference**

### **Common Issues & Solutions**

| Issue | Solution |
|-------|----------|
| **"Connection refused"** | 1. Check server is running<br>2. Verify server IP<br>3. Check Windows Firewall |
| **"No route to host"** | 1. Ensure same WiFi network<br>2. Try `ping SERVER_IP`<br>3. Check network adapter |
| **"Module not found"** | 1. Run `pip install -r requirements.txt`<br>2. Run gRPC generation command |
| **"Permission denied"** | 1. Run as Administrator<br>2. Check firewall settings |
| **"Timeout"** | 1. Check network congestion<br>2. Verify port 50051 is open |

### **Quick Diagnostic Commands**
```bash
# Test Python installation
python --version

# Test dependencies
python -c "import grpc; print('gRPC OK')"

# Test server connection
python test_connection.py

# Check network connectivity
ping SERVER_IP
```

## 📊 **Expected Behavior**

### **Server (Laptop 1) Output**
```
Setting up Federated Learning Server...
Installing Python requirements...
Generating gRPC code...
Server configuration created
============================================================
SERVER SETUP COMPLETE!
============================================================
Server will run on: 192.168.1.100:50051
Starting server... (Press Ctrl+C to stop)
Federated Learning Server started on 192.168.1.100:50051
Client client-1 registered successfully
Client client-2 registered successfully
Results received from client-1: 15 itemsets
Results received from client-2: 12 itemsets
Global aggregation completed
```

### **Client Output**
```
Setting up Federated Learning Client...
Installing Python requirements...
Generating gRPC code...
Client configuration created
============================================================
CLIENT SETUP COMPLETE!
============================================================
Client ID: client-1
Server: 192.168.1.100:50051
Starting client... (Press Ctrl+C to stop)
Connected to server successfully
Local mining completed: 15 high-utility itemsets
Results sent to server
Global results received: 25 aggregated itemsets
```

## 🎯 **Success Indicators**

✅ **All laptops connected to server**  
✅ **Local FP-Growth mining completed**  
✅ **Results sent to server successfully**  
✅ **Global aggregation completed**  
✅ **No error messages in any terminal**  

## 📞 **Getting Help**

### **If Something Goes Wrong:**

1. **Check the logs** - Look for specific error messages
2. **Test connectivity** - Run `python test_connection.py`
3. **Verify network** - Ensure all laptops are on same WiFi
4. **Check firewall** - Windows Firewall might block connections
5. **Restart in order** - Server first, then clients

### **Useful Files for Debugging:**
- `network_setup_guide.md` - Detailed network troubleshooting
- `test_federated_system.py` - Comprehensive system tests
- `CLIENT_SETUP_INSTRUCTIONS.txt` - Auto-generated instructions

## 🔄 **Next Steps After Success**

1. **Use real datasets** - Replace sample data with your actual data
2. **Adjust parameters** - Modify utility thresholds and privacy settings
3. **Add more clients** - Scale to more laptops if needed
4. **Monitor performance** - Track mining time and accuracy
5. **Optimize settings** - Fine-tune for your specific use case

## 📱 **Alternative: Docker Deployment**

If you prefer Docker:
```bash
# Server (Laptop 1)
docker-compose up federated-server

# Clients (Laptops 2 & 3)
# Modify docker-compose.yml with server IP, then:
docker-compose up client-1  # or client-2
```

---

**🎉 Congratulations!** You now have a working federated learning system across 3 laptops that preserves data privacy while enabling collaborative high-utility itemset mining. 