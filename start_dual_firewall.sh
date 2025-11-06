#!/bin/bash
# Dual-Layer Firewall Startup Script
# Starts both Network Firewall and Application WAF

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     Dual-Layer Firewall System - Starting Services       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Error: Network firewall requires root privileges"
    echo "   Run: sudo ./start_dual_firewall.sh"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Run setup first."
    exit 1
fi

# Check if network firewall dependencies are installed
python3 -c "import netfilterqueue" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  netfilterqueue not installed. Installing..."
    pip install netfilterqueue scapy
fi

# Start Network Firewall in background
echo "🔧 Starting Network Layer Firewall (requires root)..."
sudo python3 network_firewall.py &
NETWORK_FW_PID=$!
echo "   Network Firewall PID: $NETWORK_FW_PID"
sleep 2

# Start Application WAF
echo "🔧 Starting Application Layer WAF (port 8081)..."
python3 Proxy_server.py &
WAF_PID=$!
echo "   WAF PID: $WAF_PID"
sleep 2

echo ""
echo "✅ Dual-Layer Firewall System Started!"
echo ""
echo "📊 Services:"
echo "   Network Firewall: Running (PID: $NETWORK_FW_PID)"
echo "   Application WAF:  Running on http://127.0.0.1:8081 (PID: $WAF_PID)"
echo ""
echo "🛑 To stop:"
echo "   sudo kill $NETWORK_FW_PID $WAF_PID"
echo "   sudo iptables -F"
echo ""
echo "Press Ctrl+C to stop all services..."

# Wait for user interrupt
trap "echo ''; echo 'Stopping services...'; sudo kill $NETWORK_FW_PID $WAF_PID 2>/dev/null; sudo iptables -F 2>/dev/null; exit" INT TERM

# Keep script running
wait

