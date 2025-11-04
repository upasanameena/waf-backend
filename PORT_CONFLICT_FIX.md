# Fix: Port 8080 Already in Use

## Problem
Port 8080 is already being used (likely by your UI server).

## Solution Options

### Option 1: Change WAF Port (Recommended)

The WAF has been updated to use port **8081** instead of 8080.

**Just run:**
```bash
python Proxy_server.py
```

**WAF will now run on:** `http://127.0.0.1:8081`  
**UI server runs on:** `http://localhost:8080`

---

### Option 2: Kill Process Using Port 8080

**Find what's using port 8080:**
```bash
sudo lsof -i :8080
# OR
sudo netstat -tulpn | grep :8080
```

**Kill the process:**
```bash
# Replace <PID> with the number from above command
sudo kill -9 <PID>
```

**Then run WAF:**
```bash
python Proxy_server.py
```

---

### Option 3: Use Different Port (Custom)

If you want to use a different port, edit `Proxy_server.py`:

```python
# Change this line (around line 155):
host, port = '127.0.0.1', 8000  # Use port 8000 or any available port
```

---

## Current Port Configuration

| Service | Port | URL |
|---------|------|-----|
| **UI Server** | 8080 | http://localhost:8080 |
| **API Server** | 5174 | http://localhost:5174 |
| **WAF Server** | 8081 | http://127.0.0.1:8081 |

---

## Testing WAF on New Port

```bash
# Test good request
curl http://127.0.0.1:8081/test

# Test malicious request
curl "http://127.0.0.1:8081/?id=1' OR '1'='1"
```

---

## Complete Setup (All Services)

**Terminal 1 - WAF Server:**
```bash
cd ~/Documents/projects/Web_Application_Firewall
source venv/bin/activate
python Proxy_server.py
# Runs on: http://127.0.0.1:8081
```

**Terminal 2 - API Server:**
```bash
cd ~/capstone
export BACKEND_ROOT=/home/kali/Documents/projects/Web_Application_Firewall
npm run api
# Runs on: http://localhost:5174
```

**Terminal 3 - UI Server:**
```bash
cd ~/capstone
npm run dev
# Runs on: http://localhost:8080
```

---

## Quick Check: What's Using Ports

```bash
# Check port 8080
sudo lsof -i :8080

# Check port 8081
sudo lsof -i :8081

# Check port 5174
sudo lsof -i :5174
```

---

## Summary

✅ **WAF port changed to 8081** - No more conflicts!  
✅ **UI stays on 8080** - Your visualization dashboard  
✅ **API on 5174** - CSV data server

Just run `python Proxy_server.py` and it will work!

