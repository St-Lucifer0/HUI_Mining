# GitHub Deployment Guide for Federated HUI Mining System

## Overview
Using GitHub for multi-laptop deployment provides better version control, easier file distribution, and ensures both machines have identical code.

## Step 1: Prepare Your Repository

### 1.1 Check .gitignore
The `.gitignore` file has been configured to exclude:
- Virtual environments (`.venv/`)
- Log files (`*.log`)
- Large dataset files (`*.csv` - except samples)
- Results files (`fp_growth_results_*.txt`)
- IDE and OS specific files

### 1.2 Before Pushing to GitHub
```cmd
# Check what files will be committed
git status

# Add all files (respecting .gitignore)
git add .

# Commit your changes
git commit -m "Initial federated HUI mining system"

# Push to GitHub
git push origin main
```

## Step 2: Client Laptop Setup via GitHub

### 2.1 Install Prerequisites on Client Laptop
- Git for Windows
- Python 3.7+
- Command Prompt or PowerShell

### 2.2 Clone Repository
```cmd
# Navigate to desired location
cd "C:\Users\[USERNAME]\Desktop"

# Clone your repository
git clone https://github.com/[YOUR-USERNAME]/[YOUR-REPO-NAME].git

# Navigate to project directory
cd [YOUR-REPO-NAME]
```

### 2.3 Setup Environment
```cmd
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Network Configuration

### 3.1 Configure Firewall (Both Machines)
Run as Administrator:
```cmd
# Run the firewall setup script
setup_firewall.bat
```

Or manually:
```cmd
netsh advfirewall firewall add rule name="HUI Mining API Server" dir=in action=allow protocol=TCP localport=5000
netsh advfirewall firewall add rule name="HUI Mining Federated Server" dir=in action=allow protocol=TCP localport=50051
```

### 3.2 Test Network Connectivity
```cmd
# Run network troubleshooting script
network_troubleshoot.bat
```

## Step 4: Running the System

### 4.1 On Server Laptop (Main Machine)
```cmd
# Navigate to project directory
cd "C:\Users\User\PycharmProjects\FP-GROWTH(Enhanced)_for_HUIs"

# Activate virtual environment
.venv\Scripts\activate

# Start server
python integrated_system.py --mode server

# Or use batch script
start_integrated_server.bat
```

### 4.2 On Client Laptop
```cmd
# Navigate to project directory
cd "C:\Users\[USERNAME]\Desktop\[YOUR-REPO-NAME]"

# Activate virtual environment
.venv\Scripts\activate

# Start client (interactive)
start_integrated_client.bat

# Or manually with specific parameters
python integrated_system.py --mode client --client-id client-4 --server-address [SERVER-IP] --federated-port 50051
```

## Step 5: Updating Code

### 5.1 When You Make Changes (Server Machine)
```cmd
# Add and commit changes
git add .
git commit -m "Description of changes"
git push origin main
```

### 5.2 Update Client Machine
```cmd
# Navigate to project directory
cd "C:\Users\[USERNAME]\Desktop\[YOUR-REPO-NAME]"

# Pull latest changes
git pull origin main

# Reinstall dependencies if requirements.txt changed
pip install -r requirements.txt
```

## Advantages of GitHub Approach

✅ **Version Control**: Track all changes and easily revert if needed
✅ **Synchronization**: Both machines always have the same code version
✅ **No File Transfer Errors**: Git ensures all files are correctly copied
✅ **Easy Updates**: Simple `git pull` to get latest changes
✅ **Backup**: Your code is safely stored in the cloud
✅ **Collaboration**: Easy to share with team members

## Troubleshooting

### Git Issues
- **Authentication**: Use GitHub Personal Access Token for HTTPS
- **Large Files**: Use Git LFS for large datasets if needed
- **Conflicts**: Resolve merge conflicts before pushing

### Network Issues
- **Same as before**: Firewall, network connectivity, IP addresses
- **GitHub doesn't fix network issues**: Still need proper network setup

### File Issues
- **Missing Files**: Check `.gitignore` - might be excluding needed files
- **Permissions**: Ensure proper file permissions after cloning

## Security Considerations

⚠️ **Never commit**:
- API keys or passwords
- Local IP addresses in config files
- Personal data or sensitive datasets
- Virtual environment folders

✅ **Safe to commit**:
- Source code
- Configuration templates
- Documentation
- Sample datasets (small)
- Requirements.txt

## Next Steps

1. Push your current code to GitHub
2. Test the GitHub clone process on the client laptop
3. Verify the federated system works with GitHub-deployed code
4. Use this workflow for future updates and deployments
