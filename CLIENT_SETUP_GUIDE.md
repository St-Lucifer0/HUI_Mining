# Client Laptop Setup Guide

## Prerequisites
1. Both laptops must be on the same network (WiFi or LAN)
2. Windows Firewall must allow communication on ports 5000 and 50051
3. Python 3.7+ installed on both machines

## Step 1: Get Project Files (Choose Method A or B)

### Method A: GitHub Clone (RECOMMENDED)
1. Ensure Git is installed on the client laptop
2. Open Command Prompt and navigate to desired location:
   ```cmd
   cd "C:\Users\[USERNAME]\Desktop"
   ```
3. Clone the repository:
   ```cmd
   git clone https://github.com/[YOUR-USERNAME]/[YOUR-REPO-NAME].git
   cd [YOUR-REPO-NAME]
   ```

### Method B: Manual Copy (Alternative)
1. Copy the ENTIRE project folder `FP-GROWTH(Enhanced)_for_HUIs` to the client laptop
2. Place it in a location like `C:\Users\[USERNAME]\Desktop\HUI_Mining-master\`
3. Ensure all files are present, especially:
   - `integrated_system.py`
   - `start_integrated_client.bat`
   - All `.py` modules
   - `requirements.txt`

## Step 2: Setup Python Environment on Client
```cmd
# Navigate to project directory
cd "C:\Users\[USERNAME]\Desktop\HUI_Mining-master"

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Network Configuration

### Find Server IP Address
On the SERVER laptop, run:
```cmd
ipconfig
```
Look for the IPv4 address (e.g., 192.168.1.100)

### Test Network Connectivity
On the CLIENT laptop, test connection:
```cmd
ping [SERVER_IP_ADDRESS]
```
If ping fails, check:
- Both devices on same network
- Windows Firewall settings
- Router/network configuration

### Configure Windows Firewall
On BOTH laptops, allow these ports:
1. Open Windows Defender Firewall
2. Click "Advanced settings"
3. Create new Inbound Rules for:
   - Port 5000 (TCP) - API Server
   - Port 50051 (TCP) - Federated Learning

## Step 4: Start the System

### On SERVER laptop:
```cmd
cd "C:\Users\User\PycharmProjects\FP-GROWTH(Enhanced)_for_HUIs"
.venv\Scripts\activate
python integrated_system.py --mode server
```

### On CLIENT laptop:
```cmd
cd "C:\Users\[USERNAME]\Desktop\HUI_Mining-master"
.venv\Scripts\activate
start_integrated_client.bat
```

Or manually:
```cmd
python integrated_system.py --mode client --client-id client-4 --server-address [SERVER_IP] --federated-port 50051
```

## Step 5: Verify Connection
- Server should show: "API Server: http://localhost:5000"
- Server should show: "Federated Server: 0.0.0.0:50051"
- Client should connect without errors
- Check web interface at: http://[SERVER_IP]:5000

## Troubleshooting

### "File not found" errors:
- Ensure you're in the correct directory
- Verify all project files are copied
- Check file paths in error messages

### Network connection issues:
- Verify IP addresses with `ipconfig`
- Test ping between machines
- Check firewall settings
- Ensure both on same network

### Import errors:
- Reinstall requirements: `pip install -r requirements.txt`
- Check Python version compatibility
- Verify virtual environment is activated

### Permission errors:
- Run Command Prompt as Administrator
- Check file/folder permissions
- Ensure antivirus isn't blocking files
