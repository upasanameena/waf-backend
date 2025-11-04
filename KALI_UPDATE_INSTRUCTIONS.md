# Update WAF on Kali Linux - Manual Instructions

## Quick Fix: Copy Changes to Kali

### Option 1: Copy Updated File from Host to Kali (Easiest)

**On Windows (PowerShell):**
```powershell
# Copy the updated Proxy_server.py to Kali
scp F:\Project\kali-vm-project-main\Proxy_server.py kali@VM_IP:~/Documents/projects/Web_Application_Firewall/
```

**On Kali:**
```bash
# Verify file was copied
cd ~/Documents/projects/Web_Application_Firewall
ls -la Proxy_server.py
```

---

### Option 2: Manual Edit on Kali (If Option 1 doesn't work)

**On Kali Linux, edit the file:**

```bash
cd ~/Documents/projects/Web_Application_Firewall
nano Proxy_server.py
```

**Make these changes:**

#### Change 1: Update badwords list (around line 11)

**FIND:**
```python
badwords = ['sleep', 'uid', 'select', 'waitfor', 'delay', 'system', 'union', 
            'order by', 'group by', 'admin', 'drop', 'script']
```

**REPLACE WITH:**
```python
# List of suspicious keywords - SQL injection and XSS patterns
badwords = [
    # SQL Injection keywords
    'select', 'union', 'or', 'and', 'where', 'from', 'insert', 'update', 'delete',
    'drop', 'table', 'database', 'exec', 'execute', 'script', 'waitfor', 'delay',
    'sleep', 'order by', 'group by', 'having', 'join', 'inner join', 'outer join',
    # XSS and Scripting
    'script', '<script', '</script>', 'javascript:', 'onerror', 'onclick', 'onload',
    'alert', 'eval', 'document.cookie', 'document.write',
    # Other suspicious patterns
    'admin', 'uid', 'password', 'passwd', 'root', 'system', 'cmd', 'command',
    'shell', 'phpinfo', 'base64', 'char(', 'ascii('
]
```

#### Change 2: Update do_GET method (around line 120)

**FIND:**
```python
    def do_GET(self):
        path = self.path
        body = ""  # GET requests don't have a body

        # Extract features and check model
        features = np.array(ExtractFeatures(path, body)).reshape(1, -1)
        prediction = model.predict(features)[0]

        # Check badwords
        found_badwords = [word for word in badwords if word.lower() in path.lower()]

        # Append payload to respective CSV
        if prediction == 1 or found_badwords:
            append_payload_to_csv(MALICIOUS_CSV, path, body)
            reason = f"Blocked because of {' & '.join(found_badwords)}" if found_badwords else "Blocked by ML model"
            self.send_response(403, "Forbidden")
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(f"Malicious request detected!\nReason: {reason}".encode())
            print(f"[BLOCKED] {self.client_address[0]} {path} --> {reason}")
        else:
            # Append benign payload
            append_payload_to_csv(BENIGN_CSV, path, body)

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Nothing malicious detected. PASSED!")
            print(f"[PASSED] {self.client_address[0]} {path}")
```

**REPLACE WITH:**
```python
    def do_GET(self):
        path = self.path
        body = ""  # GET requests don't have a body

        # Extract features and check model
        features = np.array(ExtractFeatures(path, body)).reshape(1, -1)
        prediction = model.predict(features)[0]
        
        # Get prediction probability for better detection
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(features)[0]
            malicious_prob = proba[1] if len(proba) > 1 else proba[0]
        else:
            malicious_prob = 0.5 if prediction == 1 else 0.0

        # Check badwords (case-insensitive)
        path_lower = path.lower()
        found_badwords = [word for word in badwords if word.lower() in path_lower]
        
        # Additional SQL injection pattern detection
        sql_patterns = [
            "' or '", "' or 1", "or '1'='1", "or 1=1", "or '1'='1'",
            "union select", "union all", "' union", "'; --", "'; #",
            "1' or '1'='1", "1' or 1=1", "' or 1=1 --", "admin'--"
        ]
        found_sql_patterns = [pattern for pattern in sql_patterns if pattern.lower() in path_lower]

        # Combine all detection methods
        is_malicious = (prediction == 1) or found_badwords or found_sql_patterns or (malicious_prob > 0.7)

        # Append payload to respective CSV
        if is_malicious:
            append_payload_to_csv(MALICIOUS_CSV, path, body)
            
            # Build detailed reason
            reasons = []
            if found_badwords:
                reasons.append(f"Badwords: {', '.join(found_badwords)}")
            if found_sql_patterns:
                reasons.append(f"SQL pattern: {', '.join(found_sql_patterns)}")
            if prediction == 1:
                reasons.append(f"ML model (confidence: {malicious_prob:.2%})")
            if not reasons:
                reasons.append("High ML confidence")
            
            reason = " | ".join(reasons) if reasons else "Malicious pattern detected"
            
            self.send_response(403, "Forbidden")
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(f"Malicious request detected!\nReason: {reason}".encode())
            print(f"[BLOCKED] {self.client_address[0]} {path}")
            print(f"  └─ Reason: {reason}")
        else:
            # Append benign payload
            append_payload_to_csv(BENIGN_CSV, path, body)

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Nothing malicious detected. PASSED!")
            print(f"[PASSED] {self.client_address[0]} {path} (ML: {prediction}, Prob: {malicious_prob:.2%})")
```

**Save and exit:**
- In nano: Press `Ctrl+X`, then `Y`, then `Enter`

---

### Option 3: Use Git (If you pushed to GitHub)

**On Kali:**
```bash
cd ~/Documents/projects/Web_Application_Firewall
git pull origin main  # or master, depending on your branch
```

---

## After Making Changes

**Restart the WAF server:**

```bash
# Stop current server (Ctrl+C if running)

# Activate venv
source venv/bin/activate

# Restart WAF
python Proxy_server.py
```

**Test it:**
```bash
curl "http://127.0.0.1:8081/?id=1' OR '1'='1"
```

**Should now show:**
```
Malicious request detected!
Reason: Badwords: or | SQL pattern: or '1'='1
```

---

## Quick Copy-Paste for Nano Editor

If using nano on Kali, here's the exact sequence:

1. **Open file:**
   ```bash
   cd ~/Documents/projects/Web_Application_Firewall
   nano Proxy_server.py
   ```

2. **Search for badwords (Ctrl+W, type "badwords", Enter)**

3. **Replace the badwords list** (select and replace the entire list)

4. **Search for "def do_GET" (Ctrl+W, type "def do_GET", Enter)**

5. **Replace the entire do_GET method** with the new code above

6. **Save: Ctrl+X, Y, Enter**

---

## Verify Changes

After updating, check that the file has the changes:

```bash
# Check badwords list includes 'or'
grep -n "'or'" Proxy_server.py

# Check SQL patterns are added
grep -n "sql_patterns" Proxy_server.py

# Should show the new code
```

---

## Summary

✅ **Option 1 (SCP):** Fastest - copy file from Windows to Kali  
✅ **Option 2 (Manual):** Edit directly on Kali using nano  
✅ **Option 3 (Git):** If using Git, pull the latest changes

Choose whichever method works best for you!


