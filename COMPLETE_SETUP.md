# Complete Dual-Layer Firewall System - Setup Instructions

## 🚀 Quick Start (All Services)

### Step 1: Install Dependencies on Kali

```bash
# Navigate to WAF project
cd ~/Documents/projects/Web_Application_Firewall

# Activate venv
source venv/bin/activate

# Install network firewall dependencies
pip install netfilterqueue scapy

# If netfilterqueue fails:
sudo apt install -y libnetfilter-queue-dev python3-dev
pip install netfilterqueue
```

### Step 2: Load Kernel Modules

```bash
sudo modprobe nfnetlink_queue
sudo modprobe iptable_nat
sudo modprobe iptable_filter
```

### Step 3: Start All Services (4 Terminals Required)

**Terminal 1 - Network Firewall (NEEDS ROOT):**
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

### Step 4: Open Dashboard

```bash
xdg-open http://localhost:8080
```

---

## ✅ Verification Commands

### Check Network Firewall is Running:
```bash
ps aux | grep network_firewall
sudo iptables -L -n | grep NFQUEUE
```

### Check Application WAF is Running:
```bash
ps aux | grep Proxy_server
curl http://127.0.0.1:8081/test
```

### Check API is Working:
```bash
curl http://localhost:5174/api/stats/get-requests
curl http://localhost:5174/api/stats/network-firewall
```

### Generate Test Traffic:
```bash
# Network traffic (should be logged by network firewall)
ping 8.8.8.8
curl http://127.0.0.1:8081/test

# Application attacks (should be blocked by WAF)
curl "http://127.0.0.1:8081/?id=1' OR '1'='1"
curl -X POST http://127.0.0.1:8081/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin' OR '1'='1&password=x"
```

### Check CSV Files:
```bash
ls -la ~/Documents/projects/Web_Application_Firewall/network_blocked.csv
ls -la ~/Documents/projects/Web_Application_Firewall/network_allowed.csv
ls -la ~/Documents/projects/Web_Application_Firewall/Data_Collection/*.csv
```

---

## 📊 Expected Dashboard Output

After running all services and generating traffic, you should see:

1. **URL Filter Analysis (GET)** - Good vs Bad URLs
2. **Payload Classification (POST)** - Benign vs Malware payloads
3. **Network Layer Firewall** - Allowed vs Blocked packets
4. **ML Model Training Overview** - Training progress over time

All sections update automatically every 10 seconds.

---

## 🛑 Stopping Services

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

## ⚠️ Troubleshooting

### Network Firewall Not Working:
- Must run as root: `sudo python3 network_firewall.py`
- Check modules: `lsmod | grep nfnetlink`
- Check iptables: `sudo iptables -L -n`

### No Data in Visualization:
- Verify CSV files exist and have data
- Check API can read files: `curl http://localhost:5174/api/debug/paths`
- Ensure BACKEND_ROOT is set correctly

### Port Conflicts:
- Network firewall: uses NFQUEUE (no port)
- WAF: port 8081
- API: port 5174
- UI: port 8080

---

## 🎯 Complete System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client Traffic                        │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Network Firewall    │  ← Packet-level filtering
        │  (netfilterqueue)    │  ← Root required
        └──────────┬───────────┘
                   │ (Allowed packets)
                   ▼
        ┌──────────────────────┐
        │  Application WAF      │  ← HTTP-level analysis
        │  (Proxy_server.py)   │  ← Port 8081
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  CSV Logging          │  ← All decisions logged
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  API Server           │  ← Reads CSVs, serves JSON
        │  (server.mjs)         │  ← Port 5174
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  UI Dashboard         │  ← Real-time visualization
        │  (React + Recharts)   │  ← Port 8080
        └──────────────────────┘
```

---

## ✨ You're All Set!

Your complete dual-layer firewall system is ready with:
- ✅ Network layer packet filtering
- ✅ Application layer HTTP analysis
- ✅ ML-based detection at both layers
- ✅ Real-time visualization dashboard
- ✅ Automated retraining
- ✅ Complete logging system

**Start all 4 services and open the dashboard to see it in action!**

