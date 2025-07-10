# Updated Client Setup Instructions
# =================================

## Server Information
- **Server IP Address**: 172.20.10.14
- **Server Port**: 50051
- **Protocol**: gRPC

## Quick Start (Recommended)

### Step 1: Generate gRPC Code
```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. federated_learning.proto
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Test System
```bash
python test_federated_system.py
```

### Step 4: Test Network Connectivity
```bash
python network_troubleshooter.py 172.20.10.14 50051
```

## Client Setup for Each Laptop

### For Laptop 2 (Client 1):
```bash
# Basic setup
python setup_client.py --client-id client-1 --server-address 172.20.10.14

# With dataset (if available)
python setup_client.py --client-id client-1 --server-address 172.20.10.14 --dataset-path generated_foodmart_dataset.csv
```

### For Laptop 3 (Client 2):
```bash
# Basic setup
python setup_client.py --client-id client-2 --server-address 172.20.10.14

# With dataset (if available)
python setup_client.py --client-id client-2 --server-address 172.20.10.14 --dataset-path client2_foodmart_dataset.csv
```

## Network Requirements

### Windows Firewall Setup
If you encounter connection issues, add firewall rules:

**Option 1: Automatic (Recommended)**
```bash
python network_troubleshooter.py 172.20.10.14 50051
# Follow the prompts to add firewall rules automatically
```

**Option 2: Manual**
```cmd
# Run as Administrator
netsh advfirewall firewall add rule name="FederatedLearning_50051" dir=in action=allow protocol=TCP localport=50051
netsh advfirewall firewall add rule name="FederatedLearning_50051_out" dir=out action=allow protocol=TCP localport=50051
```

### Network Configuration
- All laptops must be on the same network
- Ensure port 50051 is not blocked by antivirus software
- Check that the server IP address is correct

## Troubleshooting

### Issue 1: "Local Mining FAILED"
**Problem**: Data format mismatch in sample data
**Solution**: ✅ **FIXED** - Updated sample data format in federated_client.py

### Issue 2: "Docker Build FAILED"
**Problem**: Docker not installed or not in PATH
**Solution**: Docker is optional for this setup. The system works without Docker.

### Issue 3: Connection Timeout
**Problem**: Network connectivity issues
**Solutions**:
1. Run network diagnostics: `python network_troubleshooter.py 172.20.10.14`
2. Check firewall settings
3. Verify server is running: `python setup_server.py`
4. Test basic connectivity: `ping 172.20.10.14`

### Issue 4: gRPC Import Errors
**Problem**: Generated protobuf files missing or outdated
**Solution**:
```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. federated_learning.proto
```

## Testing Connection

### Simple Connection Test
```python
import grpc
channel = grpc.insecure_channel('172.20.10.14:50051')
print('Connection successful')
```

### Advanced Connection Test
```bash
python test_connection.py
```

## Expected Test Results

After running `python test_federated_system.py`, you should see:
```
✓ gRPC Generation PASSED
✓ Module Imports PASSED
✓ Server Creation PASSED
✓ Client Creation PASSED
✓ Local Mining PASSED (FIXED)
✓ Privacy-Preserving Mining PASSED
⚠ Docker Build FAILED (Optional)
⚠ Docker Compose FAILED (Optional)

Overall: 6/8 tests passed
```

## Running the Complete System

### 1. Start Server (on Server Laptop)
```bash
python setup_server.py
```

### 2. Start Clients (on Client Laptops)
```bash
# Client 1
python setup_client.py --client-id client-1 --server-address 172.20.10.14

# Client 2  
python setup_client.py --client-id client-2 --server-address 172.20.10.14
```

### 3. Monitor Progress
- Server logs will show client registrations
- Client logs will show mining progress
- Results will be saved to the `results/` directory

## Quick Test Script

Use the provided batch script for quick testing:
```bash
quick_test.bat 172.20.10.14
```

This will:
1. Generate gRPC code
2. Run system tests
3. Test network connectivity
4. Provide next steps

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Run `python network_troubleshooter.py 172.20.10.14`
3. Verify all dependencies are installed: `pip install -r requirements.txt`
4. Ensure the server is running before starting clients 