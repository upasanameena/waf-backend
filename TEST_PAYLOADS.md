# Testing POST Payloads with WAF

## How to Test POST Payloads

### 1. Start WAF Server

```bash
cd ~/Documents/projects/Web_Application_Firewall
source venv/bin/activate
python Proxy_server.py
```

### 2. Test POST Requests with Payloads

#### Test Good/Benign Payload:
```bash
curl -X POST http://127.0.0.1:8081/submit \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "name=John&email=john@example.com&message=Hello"
```

**Expected:** `Nothing malicious detected. PASSED!`

---

#### Test Malicious SQL Injection Payload:
```bash
curl -X POST http://127.0.0.1:8081/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin' OR '1'='1&password=test"
```

**Expected:** `Malicious payload detected! Reason: SQL pattern: or '1'='1`

---

#### Test XSS Payload:
```bash
curl -X POST http://127.0.0.1:8081/comment \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "comment=<script>alert('XSS')</script>"
```

**Expected:** `Malicious payload detected! Reason: XSS pattern: <script`

---

#### Test Command Injection Payload:
```bash
curl -X POST http://127.0.0.1:8081/search \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=test; rm -rf /"
```

**Expected:** `Malicious payload detected! Reason: Badwords: ...`

---

## Using HTML Form (Browser Testing)

Create a test HTML file:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Test WAF POST Payloads</title>
</head>
<body>
    <h2>Test Benign Payload</h2>
    <form action="http://127.0.0.1:8081/submit" method="POST">
        <input type="text" name="name" value="John Doe">
        <input type="email" name="email" value="john@example.com">
        <button type="submit">Submit (Should PASS)</button>
    </form>

    <h2>Test Malicious SQL Injection</h2>
    <form action="http://127.0.0.1:8081/login" method="POST">
        <input type="text" name="username" value="admin' OR '1'='1">
        <input type="password" name="password" value="test">
        <button type="submit">Submit (Should BLOCK)</button>
    </form>

    <h2>Test XSS Payload</h2>
    <form action="http://127.0.0.1:8081/comment" method="POST">
        <textarea name="comment"><script>alert('XSS')</script></textarea>
        <button type="submit">Submit (Should BLOCK)</button>
    </form>
</body>
</html>
```

Save as `test_payloads.html` and open in browser.

---

## Using Python Requests

```python
import requests

# Test benign payload
response = requests.post(
    'http://127.0.0.1:8081/submit',
    data={'name': 'John', 'email': 'john@example.com'}
)
print(response.text)

# Test malicious SQL injection
response = requests.post(
    'http://127.0.0.1:8081/login',
    data={'username': "admin' OR '1'='1", 'password': 'test'}
)
print(response.text)

# Test XSS
response = requests.post(
    'http://127.0.0.1:8081/comment',
    data={'comment': "<script>alert('XSS')</script>"}
)
print(response.text)
```

---

## Using JavaScript (Browser Console)

```javascript
// Test benign payload
fetch('http://127.0.0.1:8081/submit', {
    method: 'POST',
    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
    body: 'name=John&email=john@example.com'
})
.then(r => r.text())
.then(console.log);

// Test malicious payload
fetch('http://127.0.0.1:8081/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
    body: "username=admin' OR '1'='1&password=test"
})
.then(r => r.text())
.then(console.log);
```

---

## Check Generated CSV Files

After testing, check the payloads:

```bash
# View benign payloads
cat benign_payloads.csv | tail -5

# View malicious payloads
cat malicious_payloads.csv | tail -5

# Count payloads
wc -l benign_payloads.csv
wc -l malicious_payloads.csv
```

---

## Common POST Payload Test Cases

### SQL Injection:
```bash
# Basic SQL injection
-d "user=admin' OR '1'='1"

# Union-based
-d "id=1 UNION SELECT * FROM users"

# Comment-based
-d "id=1; --"

# Time-based
-d "id=1; WAITFOR DELAY '00:00:05'"
```

### XSS:
```bash
# Basic XSS
-d "comment=<script>alert(1)</script>"

# Event handler
-d "name=<img src=x onerror=alert(1)>"

# JavaScript protocol
-d "url=javascript:alert(1)"
```

### Command Injection:
```bash
# Basic command injection
-d "cmd=test; ls -la"

# Pipe command
-d "query=test | cat /etc/passwd"

# Backtick execution
-d "input=test `whoami`"
```

---

## Expected Output in Terminal

**When POST is blocked:**
```
[BLOCKED POST] 127.0.0.1 /login
  └─ Payload: username=admin' OR '1'='1&password=test
  └─ Reason: SQL pattern: or '1'='1
```

**When POST passes:**
```
[PASSED POST] 127.0.0.1 /submit (ML: 0, Prob: 12.34%)
```

---

## Summary

✅ **WAF now handles POST requests**  
✅ **Analyzes payload body for malicious patterns**  
✅ **Checks SQL injection, XSS, and badwords**  
✅ **Saves to `benign_payloads.csv` or `malicious_payloads.csv`**

Just run `python Proxy_server.py` and start testing POST requests!


