#!/bin/bash

#######################################################################
# DEPLOYMENT VALIDATION SCRIPT
# Tests all critical endpoints and configurations
#######################################################################

echo "═══════════════════════════════════════════════════════════"
echo "  🧪 VerzekAutoTrader Deployment Validation"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test results
PASSED=0
FAILED=0

# API Base URL
API_URL="https://api.verzekinnovative.com"

# Function to test endpoint
test_endpoint() {
    local name="$1"
    local url="$2"
    local expected="$3"
    
    echo -n "Testing $name... "
    
    response=$(curl -s "$url" 2>/dev/null || echo "ERROR")
    
    if echo "$response" | grep -q "$expected"; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        echo "  Expected: $expected"
        echo "  Got: $response"
        ((FAILED++))
        return 1
    fi
}

# Function to test HTTP status
test_http_status() {
    local name="$1"
    local url="$2"
    local expected="$3"
    
    echo -n "Testing $name... "
    
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$status" == "$expected" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $status)"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (Expected: $expected, Got: $status)"
        ((FAILED++))
        return 1
    fi
}

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  SSL & HTTPS Tests${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Test HTTP redirect to HTTPS
test_http_status "HTTP Redirect" "http://api.verzekinnovative.com/api/health" "301"

# Test HTTPS connection
test_http_status "HTTPS Connection" "$API_URL/api/health" "200"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  API Endpoint Tests${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Test health endpoint
test_endpoint "Health Check" "$API_URL/api/health" "ok"

# Test CAPTCHA generation
test_endpoint "CAPTCHA Generation" "$API_URL/api/captcha/generate" "captcha_hash"

# Test app config endpoint
test_endpoint "App Config" "$API_URL/api/app-config" "version"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Service Status Tests${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -n "Checking API service... "
if systemctl is-active --quiet verzek-api.service; then
    echo -e "${GREEN}✓ RUNNING${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ NOT RUNNING${NC}"
    ((FAILED++))
fi

echo -n "Checking Nginx service... "
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ RUNNING${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ NOT RUNNING${NC}"
    ((FAILED++))
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  SSL Certificate Tests${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -n "Checking SSL certificate... "
if [ -d "/etc/letsencrypt/live/api.verzekinnovative.com" ]; then
    echo -e "${GREEN}✓ INSTALLED${NC}"
    ((PASSED++))
    
    # Check expiry
    EXPIRY=$(openssl x509 -enddate -noout -in /etc/letsencrypt/live/api.verzekinnovative.com/fullchain.pem 2>/dev/null | cut -d= -f2)
    if [ -n "$EXPIRY" ]; then
        echo "  Expires: $EXPIRY"
    fi
else
    echo -e "${RED}✗ NOT FOUND${NC}"
    ((FAILED++))
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Configuration Tests${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -n "Checking environment file... "
if [ -f "/root/api_server_env.sh" ]; then
    echo -e "${GREEN}✓ EXISTS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ NOT FOUND${NC}"
    ((FAILED++))
fi

echo -n "Checking Firebase key... "
if [ -f "/root/firebase_key.json" ]; then
    echo -e "${GREEN}✓ EXISTS${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ NOT FOUND${NC} (optional)"
fi

echo -n "Checking log directory... "
if [ -d "/root/api_server/logs" ]; then
    echo -e "${GREEN}✓ EXISTS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ NOT FOUND${NC}"
    ((FAILED++))
fi

echo -n "Checking log rotation... "
if [ -f "/etc/logrotate.d/verzek" ]; then
    echo -e "${GREEN}✓ CONFIGURED${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ NOT CONFIGURED${NC}"
fi

echo -n "Checking auto-restart cron... "
if crontab -l 2>/dev/null | grep -q "verzek-api.service"; then
    echo -e "${GREEN}✓ CONFIGURED${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ NOT CONFIGURED${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Performance Tests${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -n "Testing response time... "
START=$(date +%s%N)
curl -s "$API_URL/api/health" > /dev/null 2>&1
END=$(date +%s%N)
RESPONSE_TIME=$(( (END - START) / 1000000 ))

if [ $RESPONSE_TIME -lt 1000 ]; then
    echo -e "${GREEN}✓ EXCELLENT${NC} (${RESPONSE_TIME}ms)"
    ((PASSED++))
elif [ $RESPONSE_TIME -lt 2000 ]; then
    echo -e "${YELLOW}✓ ACCEPTABLE${NC} (${RESPONSE_TIME}ms)"
    ((PASSED++))
else
    echo -e "${RED}✗ SLOW${NC} (${RESPONSE_TIME}ms)"
    ((FAILED++))
fi

# Summary
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Test Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${GREEN}Passed: $PASSED${NC}"
echo -e "  ${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED - DEPLOYMENT VALIDATED${NC}"
    echo ""
    exit 0
else
    echo -e "${YELLOW}⚠️  SOME TESTS FAILED - REVIEW CONFIGURATION${NC}"
    echo ""
    exit 1
fi
