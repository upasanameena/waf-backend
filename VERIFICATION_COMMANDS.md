# Complete Verification Commands - Dual-Layer Firewall

## 🎯 Quick Verification Checklist

Run these commands to verify everything is working:

### 1. Check All Services Are Running

```bash
# Network Firewall (should show process)
ps aux | grep network_firewall | grep -v grep

# Application WAF (should show process)
ps aux | grep Proxy_server | grep -v grep

# API Server (should respond)
curl http://localhost:5174/api/debug/paths

# UI Server (should be accessible)
curl http://localhost:8080 | head -20
```

### 2. Test Network Firewall

```bash
# Generate network traffic
ping -c 5 8.8.8.8

# Check if packets are logged
tail -5 ~/Documents/projects/Web_Application_Firewall/network_allowed.csv
tail -5 ~/Documents/projects/Web_Application_Firewall/network_blocked.csv
```

### 3. Test Application WAF

```bash
# Good request (should PASS)
curl http://127.0.0.1:8081/test

# SQL injection (should BLOCK)
curl "http://127.0.0.1:8081/?id=1' OR '1'='1"

# XSS (should BLOCK)
curl "http://127.0.0.1:8081/?name=<script>alert(1)</script>"

# POST attack (should BLOCK)
curl -X POST http://127.0.0.1:8081/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin' OR '1'='1&password=x"
```

### 4. Check API Endpoints

```bash
# GET stats
curl http://localhost:5174/api/stats/get-requests

# POST stats
curl http://localhost:5174/api/stats/post-payloads

# Network stats
curl http://localhost:5174/api/stats/network-firewall

# Training metrics
curl "http://localhost:5174/api/metrics/training?chunkSize=100"
```

### 5. Verify CSV Files Have Data

```bash
cd ~/Documents/projects/Web_Application_Firewall

# Count rows in each CSV
echo "Network Firewall:"
wc -l network_blocked.csv network_allowed.csv

echo "Application WAF:"
wc -l Data_Collection/Good_req.csv Data_Collection/Bad_req.csv
wc -l benign_payloads.csv malicious_payloads.csv
```

### 6. Check Dashboard Visualization

Open browser: `http://localhost:8080`

**Expected sections:**
- ✅ URL Filter Analysis (GET) - Shows good vs bad counts
- ✅ Payload Classification (POST) - Shows benign vs malware counts
- ✅ Network Layer Firewall - Shows allowed vs blocked packets
- ✅ ML Model Training Overview - Shows training progress

All should update automatically every 10 seconds.

---

## 🔧 Troubleshooting Commands

### If Network Firewall Not Working:

```bash
# Check if running as root
ps aux | grep network_firewall

# Check iptables rules
sudo iptables -L -n -v | grep NFQUEUE

# Check kernel modules
lsmod | grep nfnetlink

# Restart network firewall
sudo pkill -f network_firewall.py
sudo iptables -F
sudo python3 network_firewall.py
```

### If WAF Not Working:

```bash
# Check if running
ps aux | grep Proxy_server

# Test connection
curl http://127.0.0.1:8081/test

# Check port
netstat -tulpn | grep 8081

# Restart WAF
pkill -f Proxy_server.py
source venv/bin/activate
python3 Proxy_server.py
```

### If API Not Working:

```bash
# Check if running
ps aux | grep "node server.mjs"

# Test endpoint
curl http://localhost:5174/api/debug/paths

# Check port
netstat -tulpn | grep 5174

# Verify BACKEND_ROOT
echo $BACKEND_ROOT

# Restart API
cd ~/capstone
pkill -f "node server.mjs"
export BACKEND_ROOT=/home/kali/Documents/projects/Web_Application_Firewall
npm run api
```

### If UI Not Working:

```bash
# Check if running
ps aux | grep "vite"

# Test connection
curl http://localhost:8080

# Check port
netstat -tulpn | grep 8080

# Restart UI
cd ~/capstone
pkill -f vite
npm run dev
```

---

## 📊 Expected Output Examples

### Network Firewall Terminal:
```
[NETWORK FIREWALL] Starting network layer firewall...
[NETWORK FIREWALL] Listening on NFQUEUE 0
[NETWORK BLOCKED] 192.168.1.100:12345 -> 127.0.0.1:8081 | Reason: Suspicious port: 22
```

### WAF Terminal:
```
Starting WAF server on http://127.0.0.1:8081
[BLOCKED] 127.0.0.1 /?id=1' OR '1'='1
  └─ Reason: SQLi | Badwords: or
[PASSED] 127.0.0.1 /test (ML: 0, Prob: 12.34%)
```

### API Terminal:
```
CSV read-only API listening on http://localhost:5174
GET stats: good=45, bad=12
POST stats: benign=30, malicious=8
Network stats: blocked=5, allowed=120
```

---

## ✅ Success Indicators

**Everything is working if:**
1. ✅ All 4 services show running (`ps aux | grep ...`)
2. ✅ Network firewall logs packets to CSV
3. ✅ WAF blocks malicious requests and logs to CSV
4. ✅ API endpoints return JSON data
5. ✅ Dashboard shows 4 visualization sections with data
6. ✅ Dashboard updates automatically every 10 seconds

---

## 🎉 Complete System Status

| Service | Status Check | Port | Command |
|---------|-------------|------|---------|
| Network Firewall | `ps aux \| grep network_firewall` | NFQUEUE | `sudo python3 network_firewall.py` |
| Application WAF | `ps aux \| grep Proxy_server` | 8081 | `python3 Proxy_server.py` |
| API Server | `curl http://localhost:5174/api/debug/paths` | 5174 | `npm run api` |
| UI Dashboard | `curl http://localhost:8080` | 8080 | `npm run dev` |

**All services running = Complete dual-layer firewall system operational! 🚀**

