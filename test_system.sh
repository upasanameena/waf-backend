#!/bin/bash
# Complete System Test Script
# Tests both network and application layers

echo "╔══════════════════════════════════════════════════════════╗"
echo "║        Dual-Layer Firewall System - Test Script          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
PASSED=0
FAILED=0

# Function to test
test_endpoint() {
    local name=$1
    local url=$2
    local expected=$3
    
    echo -n "Testing $name... "
    response=$(curl -s -w "\n%{http_code}" "$url" 2>/dev/null)
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n1)
    
    if [[ "$status_code" == "$expected" ]]; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (got $status_code, expected $expected)"
        ((FAILED++))
        return 1
    fi
}

echo "1. Testing Application WAF (Port 8081)"
echo "─────────────────────────────────────"

test_endpoint "Good request" "http://127.0.0.1:8081/test" "200"
test_endpoint "SQL injection attack" "http://127.0.0.1:8081/?id=1' OR '1'='1" "403"
test_endpoint "XSS attack" "http://127.0.0.1:8081/?name=<script>alert(1)</script>" "403"

echo ""
echo "2. Testing API Server (Port 5174)"
echo "──────────────────────────────────"

test_endpoint "GET stats endpoint" "http://localhost:5174/api/stats/get-requests" "200"
test_endpoint "POST stats endpoint" "http://localhost:5174/api/stats/post-payloads" "200"
test_endpoint "Network stats endpoint" "http://localhost:5174/api/stats/network-firewall" "200"
test_endpoint "Debug paths endpoint" "http://localhost:5174/api/debug/paths" "200"

echo ""
echo "3. Testing CSV Files"
echo "────────────────────"

cd ~/Documents/projects/Web_Application_Firewall

files=(
    "Data_Collection/Good_req.csv"
    "Data_Collection/Bad_req.csv"
    "benign_payloads.csv"
    "malicious_payloads.csv"
    "network_blocked.csv"
    "network_allowed.csv"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        count=$(wc -l < "$file" 2>/dev/null || echo "0")
        if [ "$count" -gt "0" ]; then
            echo -e "${GREEN}✓${NC} $file exists ($count lines)"
            ((PASSED++))
        else
            echo -e "${YELLOW}⚠${NC} $file exists but empty"
        fi
    else
        echo -e "${RED}✗${NC} $file not found"
        ((FAILED++))
    fi
done

echo ""
echo "4. Testing Services Status"
echo "──────────────────────────"

services=("network_firewall.py" "Proxy_server.py" "node.*server.mjs" "vite")

for service in "${services[@]}"; do
    if ps aux | grep -v grep | grep -q "$service"; then
        echo -e "${GREEN}✓${NC} $service is running"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $service is NOT running"
        ((FAILED++))
    fi
done

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                    Test Results                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests PASSED! ($PASSED tests)${NC}"
    echo ""
    echo "🎉 Your dual-layer firewall system is fully operational!"
    echo ""
    echo "📊 Open dashboard: http://localhost:8080"
    exit 0
else
    echo -e "${RED}❌ Some tests FAILED ($FAILED failures, $PASSED passed)${NC}"
    echo ""
    echo "⚠️  Check the troubleshooting section in COMPLETE_SETUP.md"
    exit 1
fi

