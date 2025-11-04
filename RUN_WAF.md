# WAF Project - Execution Commands Guide

## Prerequisites

### 1. Install Python Dependencies

```bash
# Navigate to WAF project directory
cd ~/Documents/projects/Web_Application_Firewall
# OR if your path is different:
cd /path/to/Web_Application_Firewall

# Install required Python packages
pip3 install numpy scikit-learn pandas

# OR if you have a virtual environment:
python3 -m venv venv
source venv/bin/activate  # On Linux/Kali
pip install numpy scikit-learn pandas
```

### 2. Verify Python Installation

```bash
python3 --version  # Should be Python 3.6+
pip3 --version
```

---

## Main Execution Commands

### Option 1: Run WAF Proxy Server (Main)

**This is the main WAF server that intercepts and analyzes requests:**

```bash
# Navigate to project
cd ~/Documents/projects/Web_Application_Firewall

# Run the proxy server
python3 Proxy_server.py
```

**Expected Output:**
```
Starting WAF server on http://127.0.0.1:8080
[RETRAIN] Model retrained with X samples...
```

**Server will:**
- Listen on `http://127.0.0.1:8080`
- Intercept GET and POST requests
- Classify requests as good/bad using ML model
- Update CSV files (`good_words.csv`, `bad_words.csv`, `benign_payloads.csv`, `malicious_payloads.csv`)
- Automatically retrain the model periodically

**To Stop:** Press `Ctrl+C`

---

### Option 2: Run Test Backend (Optional)

**If you want to test the WAF with a simple backend:**

```bash
# Terminal 1: Start WAF Proxy Server
cd ~/Documents/projects/Web_Application_Firewall
python3 Proxy_server.py

# Terminal 2: Start Test Backend (Flask)
cd ~/Documents/projects/Web_Application_Firewall
python3 test_backend.py
```

**Test Backend runs on:** `http://127.0.0.1:5000`

---

## Complete Setup & Run Sequence

### Step-by-Step Commands:

```bash
# 1. Navigate to WAF project
cd ~/Documents/projects/Web_Application_Firewall

# 2. Check if Python is installed
python3 --version

# 3. Install dependencies (if not already installed)
pip3 install numpy scikit-learn pandas

# 4. Verify model file exists
ls -la training_model.pkl

# 5. Start the WAF proxy server
python3 Proxy_server.py
```

---

## Running with Virtual Environment (Recommended)

```bash
# 1. Create virtual environment
cd ~/Documents/projects/Web_Application_Firewall
python3 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install dependencies
pip install numpy scikit-learn pandas

# 4. Run WAF server
python Proxy_server.py

# 5. Deactivate when done
deactivate
```

---

## Testing the WAF

### Test Good Request:
```bash
# In another terminal while WAF is running
curl http://127.0.0.1:8080/test
# Should return: "Nothing malicious detected. PASSED!"
```

### Test Malicious Request:
```bash
# Test with SQL injection
curl "http://127.0.0.1:8080/?id=1' OR '1'='1"
# Should return: "Malicious request detected! Reason: Blocked by ML model"
```

### Test Bad Words:
```bash
# Test with bad word in URL
curl "http://127.0.0.1:8080/admin?select=*"
# Should return: "Malicious request detected! Reason: Blocked because of select"
```

---

## Check Generated CSV Files

```bash
# View good requests
cat Data_Collection/Good_req.csv | head -20

# View bad requests  
cat Data_Collection/Bad_req.csv | head -20

# View benign payloads
cat benign_payloads.csv | head -20

# View malicious payloads
cat malicious_payloads.csv | head -20

# Count rows
wc -l Data_Collection/Good_req.csv
wc -l Data_Collection/Bad_req.csv
wc -l benign_payloads.csv
wc -l malicious_payloads.csv
```

---

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'numpy'"

**Solution:**
```bash
pip3 install numpy scikit-learn pandas
```

### Issue: "FileNotFoundError: training_model.pkl"

**Solution:**
- The model file should exist in the project root
- If missing, you may need to train the model first (see README.md)

### Issue: "Address already in use" (Port 8080)

**Solution:**
```bash
# Find what's using port 8080
sudo lsof -i :8080
# Kill the process
sudo kill -9 <PID>

# OR change port in Proxy_server.py:
# host, port = '127.0.0.1', 8081  # Change 8080 to 8081
```

### Issue: "Permission denied"

**Solution:**
```bash
# Make script executable
chmod +x Proxy_server.py

# OR run with python3 explicitly
python3 Proxy_server.py
```

---

## Quick Reference Commands

| Task | Command |
|------|---------|
| Install dependencies | `pip3 install numpy scikit-learn pandas` |
| Run WAF server | `python3 Proxy_server.py` |
| Run test backend | `python3 test_backend.py` |
| Check CSV files | `ls -la *.csv Data_Collection/*.csv` |
| View logs | `tail -f Log_Files/*.log` |
| Test good request | `curl http://127.0.0.1:8080/test` |
| Test malicious request | `curl "http://127.0.0.1:8080/?id=1' OR '1'='1"` |
| Stop server | `Ctrl+C` |

---

## Running in Background (Optional)

```bash
# Run WAF server in background
nohup python3 Proxy_server.py > waf.log 2>&1 &

# Check if running
ps aux | grep Proxy_server

# View logs
tail -f waf.log

# Stop background process
pkill -f Proxy_server.py
```

---

## Integration with Visualization Dashboard

Once your WAF is running and generating CSV files:

1. **WAF running** (Terminal 1):
   ```bash
   cd ~/Documents/projects/Web_Application_Firewall
   python3 Proxy_server.py
   ```

2. **API Server running** (Terminal 2):
   ```bash
   cd ~/capstone
   export BACKEND_ROOT=/home/kali/Documents/projects/Web_Application_Firewall
   npm run api
   ```

3. **UI Server running** (Terminal 3):
   ```bash
   cd ~/capstone
   npm run dev
   ```

4. **Open browser**: `http://localhost:8080`

The visualization will show real-time data from your WAF's CSV files!

---

## File Structure Reference

```
Web_Application_Firewall/
├── Proxy_server.py          ← Main WAF server (RUN THIS)
├── test_backend.py          ← Test backend (optional)
├── training_model.pkl       ← Trained ML model
├── benign_payloads.csv      ← Generated by WAF
├── malicious_payloads.csv   ← Generated by WAF
├── Data_Collection/
│   ├── Good_req.csv         ← Generated by WAF
│   └── Bad_req.csv          ← Generated by WAF
└── Log_Files/               ← Request logs
```

---

## Summary: One-Line Start

```bash
cd ~/Documents/projects/Web_Application_Firewall && python3 Proxy_server.py
```

**That's it!** Your WAF will start intercepting and analyzing requests on port 8080.

