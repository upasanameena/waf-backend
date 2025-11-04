# Kali Linux Virtual Environment Setup

## Problem: "externally-managed-environment" Error

Kali Linux prevents installing packages system-wide. Use a virtual environment.

## Solution: Create Virtual Environment

### Step 1: Install venv support (if needed)

```bash
sudo apt install python3-venv
```

### Step 2: Create Virtual Environment

```bash
# Navigate to WAF project
cd ~/Documents/projects/Web_Application_Firewall

# Create virtual environment
python3 -m venv venv
```

### Step 3: Activate Virtual Environment

```bash
source venv/bin/activate
```

**You should see `(venv)` at the start of your prompt:**
```
(venv) ┌──(kali㉿kali)-[~/Documents/projects/Web_Application_Firewall]
```

### Step 4: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install required packages
pip install numpy scikit-learn pandas
```

### Step 5: Run WAF Server

```bash
python Proxy_server.py
```

**Note:** Use `python` (not `python3`) when venv is activated.

### Step 6: Deactivate (when done)

```bash
deactivate
```

---

## Quick One-Liner Setup

```bash
cd ~/Documents/projects/Web_Application_Firewall && \
python3 -m venv venv && \
source venv/bin/activate && \
pip install --upgrade pip && \
pip install numpy scikit-learn pandas && \
python Proxy_server.py
```

---

## Using requirements.txt

If you have `requirements.txt`:

```bash
cd ~/Documents/projects/Web_Application_Firewall
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python Proxy_server.py
```

---

## Make It Permanent (Optional)

Add alias to `~/.bashrc`:

```bash
echo 'alias waf-start="cd ~/Documents/projects/Web_Application_Firewall && source venv/bin/activate && python Proxy_server.py"' >> ~/.bashrc
source ~/.bashrc
```

Then just run: `waf-start`

---

## Troubleshooting

### "python3-venv: command not found"

```bash
sudo apt update
sudo apt install python3-venv
```

### "No module named 'venv'"

```bash
sudo apt install python3.13-venv  # or your Python version
```

### Virtual environment not activating

```bash
# Check if venv exists
ls -la venv/

# Recreate if needed
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

### Still getting errors after activation

```bash
# Make sure venv is activated (check for (venv) in prompt)
# Verify you're using venv's pip
which pip
# Should show: /home/kali/Documents/projects/Web_Application_Firewall/venv/bin/pip

# Reinstall packages
pip install --force-reinstall numpy scikit-learn pandas
```

---

## Verify Installation

```bash
# Activate venv
source venv/bin/activate

# Check installed packages
pip list | grep -E "numpy|scikit|pandas"

# Test import
python -c "import numpy; import sklearn; import pandas; print('All packages installed!')"
```

---

## Daily Usage

**Every time you want to run WAF:**

```bash
cd ~/Documents/projects/Web_Application_Firewall
source venv/bin/activate
python Proxy_server.py
```

**Or create a simple script:**

```bash
# Create start script
cat > start_waf.sh << 'EOF'
#!/bin/bash
cd ~/Documents/projects/Web_Application_Firewall
source venv/bin/activate
python Proxy_server.py
EOF

# Make executable
chmod +x start_waf.sh

# Run it
./start_waf.sh
```

