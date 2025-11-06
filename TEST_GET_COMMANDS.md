# GET Request Test Commands

## Start WAF Server

```bash
cd ~/Documents/projects/Web_Application_Firewall
source venv/bin/activate
python Proxy_server.py
```

---

## Test Commands

### Good/Benign Requests (Should PASS):

```bash
# Simple test
curl http://127.0.0.1:8081/test

# Normal query
curl "http://127.0.0.1:8081/products?id=123"

# Normal path
curl http://127.0.0.1:8081/home

# Normal search
curl "http://127.0.0.1:8081/search?q=hello"
```

---

### Malicious SQL Injection (Should BLOCK):

```bash
# SQL injection with OR
curl "http://127.0.0.1:8081/?id=1' OR '1'='1"

# SQL injection with UNION
curl "http://127.0.0.1:8081/?id=1 UNION SELECT * FROM users"

# SQL injection with comment
curl "http://127.0.0.1:8081/?id=1; --"

# SQL injection - OR 1=1
curl "http://127.0.0.1:8081/?id=1 OR 1=1"

# SQL injection - admin bypass
curl "http://127.0.0.1:8081/login?user=admin'--"
```

---

### Malicious XSS (Should BLOCK):

```bash
# XSS in query parameter
curl "http://127.0.0.1:8081/?name=<script>alert(1)</script>"

# XSS with javascript:
curl "http://127.0.0.1:8081/?url=javascript:alert(1)"

# XSS with event handler
curl "http://127.0.0.1:8081/?img=<img src=x onerror=alert(1)>"
```

---

### Malicious - Badwords (Should BLOCK):

```bash
# Admin path
curl http://127.0.0.1:8081/admin

# SELECT keyword
curl "http://127.0.0.1:8081/?query=SELECT * FROM users"

# DROP keyword
curl "http://127.0.0.1:8081/?cmd=DROP TABLE users"

# System command
curl "http://127.0.0.1:8081/?exec=system('ls')"
```

---

## Quick Test All

```bash
# Test good request
curl http://127.0.0.1:8081/test

# Test SQL injection
curl "http://127.0.0.1:8081/?id=1' OR '1'='1"

# Test XSS
curl "http://127.0.0.1:8081/?name=<script>alert(1)</script>"
```

---

## Check Results

```bash
# View blocked requests in CSV
cat Data_Collection/Bad_req.csv | tail -5

# View passed requests
cat Data_Collection/Good_req.csv | tail -5
```



