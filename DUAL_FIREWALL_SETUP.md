# Dual-Layer Firewall System - Complete Setup Guide

## Overview

This project implements a **dual-layer firewall system**:
1. **Network Layer Firewall** - Packet-level filtering using iptables + netfilterqueue
2. **Application Layer WAF** - HTTP request analysis using ML model

## Prerequisites

### System Requirements
- Kali Linux (or any Linux with root access)
- Python 3.6+
- Root/sudo access (required for network firewall)
- iptables and netfilter kernel modules

### Software Dependencies

```bash
# System packages (usually pre-installed on Kali)
sudo apt update
sudo apt install -y python3-venv iptables

# Load kernel modules
sudo modprobe nfnetlink_queue
sudo modprobe iptable_nat
sudo modprobe iptable_filter
```

---

## Installation Steps

### Step 1: Install Python Dependencies

```bash
cd ~/Documents/projects/Web_Application_Firewall

# Create/activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install all dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
python3 -c "import netfilterqueue; import scapy; print('✅ All packages installed')"
```

**If netfilterqueue installation fails:**
```bash
sudo apt install -y libnetfilter-queue-dev python3-dev
pip install netfilterqueue
```

---

## Running the System

### Option 1: Start Both Services Separately (Recommended for Testing)

**Terminal 1 - Network Firewall (requires root):**
```bash
cd ~/Documents/projects/Web_Application_Firewall
source venv/bin/activate
sudo python3 network_firewall.py
```

**Terminal 2 - Application WAF:**
```bash
cd ~/Documents/projects/Web_Application_Firewall
source venv/bin/activate
python3 Proxy_server.py
```

**Terminal 3 - API Server:**
```bash
cd ~/capstone
export BACKEND_ROOT=/home/kali/Documents/projects/Web_Application_Firewall
npm run api
```

**Terminal 4 - UI Server:**
```bash
cd ~/capstone
npm run dev
```

### Option 2: Use Startup Script (Convenient)

```bash
cd ~/Documents/projects/Web_Application_Firewall
chmod +x start_dual_firewall.sh
sudo ./start_dual_firewall.sh
```

This starts both network firewall and WAF together.

---

## Testing the System

### Test Network Firewall

**Generate network traffic:**
```bash
# In another terminal, generate packets
ping 8.8.8.8
curl http://127.0.0.1:8081/test

# Check network firewall logs
cat network_blocked.csv
cat network_allowed.csv
```

### Test Application WAF

**Good requests:**
```bash
curl http://127.0.0.1:8081/test
curl "http://127.0.0.1:8081/products?id=123"
```

**Malicious requests (should be blocked):**
```bash
curl "http://127.0.0.1:8081/?id=1' OR '1'='1"
curl "http://127.0.0.1:8081/?name=<script>alert(1)</script>"
curl -X POST http://127.0.0.1:8081/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin' OR '1'='1&password=x"
```

### Test Visualization

Open browser: `http://localhost:8080`

You should see:
- ✅ URL Filter Analysis (GET requests)
- ✅ Payload Classification (POST requests)
- ✅ Network Layer Firewall (packet filtering)
- ✅ ML Model Training Overview

---

## How It Works

### Network Layer Firewall
1. Intercepts packets using netfilterqueue
2. Extracts network features (IP, port, protocol, packet size)
3. Applies ML model + rule-based detection
4. Blocks/allows packets at network level
5. Logs to `network_blocked.csv` and `network_allowed.csv`

### Application Layer WAF
1. Receives HTTP requests (GET/POST)
2. Analyzes request path and body
3. Uses ML model + security patterns (SQLi, XSS, RCE, etc.)
4. Blocks/allows at application level
5. Logs to `Data_Collection/Good_req.csv`, `Data_Collection/Bad_req.csv`, `benign_payloads.csv`, `malicious_payloads.csv`

### Dual-Layer Protection
- **Network layer** blocks suspicious packets before they reach application
- **Application layer** analyzes HTTP content for advanced threats
- Both layers contribute to overall security

---

## Stopping the System

### If using startup script:
Press `Ctrl+C` in the script terminal

### If running separately:
```bash
# Stop network firewall
sudo pkill -f network_firewall.py
sudo iptables -F

# Stop WAF
pkill -f Proxy_server.py

# Stop API/UI
# Press Ctrl+C in respective terminals
```

---

## Troubleshooting

### "netfilterqueue not found"
```bash
sudo apt install -y libnetfilter-queue-dev python3-dev
pip install netfilterqueue
```

### "Permission denied" for network firewall
- Network firewall **must** run as root
- Use: `sudo python3 network_firewall.py`

### "Module not found" errors
```bash
sudo modprobe nfnetlink_queue
sudo modprobe iptable_nat
```

### No network firewall data in visualization
- Ensure network firewall is running (check with `ps aux | grep network_firewall`)
- Verify CSV files exist: `ls -la network_blocked.csv network_allowed.csv`
- Check API can read files: `curl http://localhost:5174/api/stats/network-firewall`

### iptables rules interfering
```bash
# Flush all rules
sudo iptables -F
sudo iptables -X

# Restart network firewall
sudo python3 network_firewall.py
```

---

## File Structure

```
Web_Application_Firewall/
├── network_firewall.py          # Network layer firewall
├── Proxy_server.py              # Application layer WAF
├── network_blocked.csv           # Network layer blocks
├── network_allowed.csv           # Network layer allows
├── Data_Collection/
│   ├── Good_req.csv             # Application layer good GET
│   └── Bad_req.csv              # Application layer bad GET
├── benign_payloads.csv           # Application layer good POST
├── malicious_payloads.csv        # Application layer bad POST
├── training_model.pkl            # ML model for WAF
└── network_firewall_model.pkl   # ML model for network (optional)
```

---

## Performance Notes

- Network firewall runs at packet level (very fast)
- Application WAF analyzes HTTP content (slightly slower)
- Both can handle typical traffic loads
- For high traffic, consider performance optimization

---

## Security Considerations

⚠️ **Important:**
- Network firewall requires root access
- Only run on trusted networks or test environments
- Test thoroughly before production use
- Monitor for false positives

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Start network firewall (`sudo python3 network_firewall.py`)
3. ✅ Start application WAF (`python3 Proxy_server.py`)
4. ✅ Start API and UI servers
5. ✅ Generate test traffic
6. ✅ View visualization dashboard

**Your dual-layer firewall system is now complete!**

