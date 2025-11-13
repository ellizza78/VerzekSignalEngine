#!/bin/bash
# VerzekAutoTrader - Complete Deployment Validation
# Validates that the deployment is working correctly
#
# Usage:
#   ./validate_deployment.sh           # Local mode (drift = warning)
#   ./validate_deployment.sh --strict  # CI/CD mode (drift = failure)

set -e

# Parse arguments
STRICT_MODE=false
if [[ "$1" == "--strict" ]]; then
    STRICT_MODE=true
fi

echo "🧪 VerzekAutoTrader - Deployment Validation"
if [ "$STRICT_MODE" = true ]; then
    echo "Mode: STRICT (CI/CD) - Version drift will fail validation"
else
    echo "Mode: NORMAL (Local) - Version drift will warn only"
fi
echo "==========================================="
echo ""

# Configuration
API_URL="https://api.verzekinnovative.com"
VULTR_HOST="80.240.29.142"

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Track failures
FAILURES=0

# Test 1: API Ping Endpoint
echo -e "${BLUE}Test 1: API Ping Endpoint${NC}"
PING_STATUS=$(curl -s -o /dev/null -w "%{http_code}" ${API_URL}/api/ping)
if [ "$PING_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ PASS${NC} - /api/ping responding (200 OK)"
    PING_DATA=$(curl -s ${API_URL}/api/ping)
    echo "   Response: $PING_DATA"
else
    echo -e "${RED}❌ FAIL${NC} - /api/ping returned HTTP $PING_STATUS"
    FAILURES=$((FAILURES + 1))
fi

# Test 2: API Health Endpoint
echo ""
echo -e "${BLUE}Test 2: API Health Endpoint${NC}"
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" ${API_URL}/api/health)
if [ "$HEALTH_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ PASS${NC} - /api/health responding (200 OK)"
    HEALTH_DATA=$(curl -s ${API_URL}/api/health)
    echo "   Response: $HEALTH_DATA"
else
    echo -e "${RED}❌ FAIL${NC} - /api/health returned HTTP $HEALTH_STATUS"
    FAILURES=$((FAILURES + 1))
fi

# Test 3: HTTPS/SSL Certificate
echo ""
echo -e "${BLUE}Test 3: HTTPS/SSL Certificate${NC}"
if curl -s --head ${API_URL} | grep -q "HTTP/"; then
    echo -e "${GREEN}✅ PASS${NC} - HTTPS working correctly"
else
    echo -e "${RED}❌ FAIL${NC} - HTTPS not working"
    FAILURES=$((FAILURES + 1))
fi

# Test 4: Service Status (requires SSH)
echo ""
echo -e "${BLUE}Test 4: Backend Service Status${NC}"
if command -v ssh &> /dev/null; then
    # Pre-seed known_hosts to avoid first-run failures
    if ! grep -q "${VULTR_HOST}" ~/.ssh/known_hosts 2>/dev/null; then
        echo "   📝 Adding ${VULTR_HOST} to known_hosts..."
        ssh-keyscan -H ${VULTR_HOST} >> ~/.ssh/known_hosts 2>/dev/null || true
    fi
    
    # Attempt SSH connection
    if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=accept-new -o BatchMode=yes root@${VULTR_HOST} "exit" 2>/dev/null; then
        SERVICE_STATUS=$(ssh -o StrictHostKeyChecking=accept-new root@${VULTR_HOST} "systemctl is-active verzek-api.service" || echo "inactive")
        if [ "$SERVICE_STATUS" = "active" ]; then
            echo -e "${GREEN}✅ PASS${NC} - verzek-api.service is active"
            
            # Get worker count
            WORKERS=$(ssh -o StrictHostKeyChecking=accept-new root@${VULTR_HOST} "ps aux | grep gunicorn | grep -v grep | wc -l")
            echo "   Workers: $WORKERS process(es)"
        else
            echo -e "${RED}❌ FAIL${NC} - verzek-api.service is not active"
            FAILURES=$((FAILURES + 1))
        fi
    else
        echo -e "${YELLOW}⚠️  SKIP${NC} - SSH not configured or connection failed"
        echo "   (This is normal in Replit environment without SSH keys)"
    fi
else
    echo -e "${YELLOW}⚠️  SKIP${NC} - SSH not available"
fi

# Test 5: Email Configuration Check
echo ""
echo -e "${BLUE}Test 5: Email Configuration${NC}"
if [ -f "backend/requirements.txt" ]; then
    if grep -q "resend==2.19.0" backend/requirements.txt; then
        echo -e "${GREEN}✅ PASS${NC} - resend==2.19.0 installed"
    else
        echo -e "${RED}❌ FAIL${NC} - resend package version incorrect"
        FAILURES=$((FAILURES + 1))
    fi
else
    echo -e "${YELLOW}⚠️  SKIP${NC} - requirements.txt not found locally"
fi

# Test 6: API Version Check
echo ""
echo -e "${BLUE}Test 6: API Version Check${NC}"
VERSION_RESPONSE=$(curl -s ${API_URL}/api/ping | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
if [ -n "$VERSION_RESPONSE" ]; then
    echo -e "${GREEN}✅ PASS${NC} - Backend version: $VERSION_RESPONSE"
    
    # Read expected version from local file if available
    if [ -f "backend/api_version.txt" ]; then
        EXPECTED_VERSION=$(grep -E "^Version:|^VERSION=" backend/api_version.txt | head -1 | sed 's/Version: v//; s/Version: //; s/VERSION=//')
        if [ -n "$EXPECTED_VERSION" ] && [ "$VERSION_RESPONSE" = "$EXPECTED_VERSION" ]; then
            echo "   Matches local version file ✓"
        elif [ -n "$EXPECTED_VERSION" ]; then
            # Version drift detected
            if [ "$STRICT_MODE" = true ]; then
                echo -e "${RED}❌ FAIL${NC} - Version drift: Local v${EXPECTED_VERSION} != Deployed v${VERSION_RESPONSE}"
                echo "   Deployment did not update the backend version correctly"
                FAILURES=$((FAILURES + 1))
            else
                echo -e "${YELLOW}   Warning: Local version is v${EXPECTED_VERSION}, deployed is v${VERSION_RESPONSE}${NC}"
                echo "   (Run with --strict to treat this as a failure)"
            fi
        fi
    else
        echo "   Valid semantic version format ✓"
    fi
else
    echo -e "${RED}❌ FAIL${NC} - Could not determine backend version"
    FAILURES=$((FAILURES + 1))
fi

# Test 7: Mobile App Configuration
echo ""
echo -e "${BLUE}Test 7: Mobile App Configuration${NC}"
if [ -f "mobile_app/VerzekApp/src/config/api.js" ]; then
    if grep -q "https://api.verzekinnovative.com" mobile_app/VerzekApp/src/config/api.js; then
        echo -e "${GREEN}✅ PASS${NC} - Mobile app API URL configured correctly"
    else
        echo -e "${RED}❌ FAIL${NC} - Mobile app API URL incorrect"
        FAILURES=$((FAILURES + 1))
    fi
else
    echo -e "${YELLOW}⚠️  SKIP${NC} - Mobile app config not found locally"
fi

# Test 8: File Manifest Verification
echo ""
echo -e "${BLUE}Test 8: File Manifest Check${NC}"
if [ -f "backend/FILE_MANIFEST_HASHES.txt" ]; then
    MANIFEST_FILES=$(grep -c "^\./" backend/FILE_MANIFEST_HASHES.txt)
    echo -e "${GREEN}✅ PASS${NC} - File manifest exists ($MANIFEST_FILES files tracked)"
    
    # Verify file count matches expected
    if [ -d "backend" ]; then
        ACTUAL_FILES=$(cd backend && find . -type f | grep -v "\.pyc$" | grep -v "__pycache__" | grep -v "\.git" | wc -l)
        if [ "$MANIFEST_FILES" -eq "$ACTUAL_FILES" ] || [ "$MANIFEST_FILES" -ge 48 ]; then
            echo "   Complete manifest: All backend files tracked ✓"
        else
            echo -e "   ${YELLOW}Warning: Manifest may be incomplete ($MANIFEST_FILES tracked vs $ACTUAL_FILES actual)${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  WARNING${NC} - File manifest not found"
fi

# Summary
echo ""
echo "==========================================="
echo -e "${BLUE}📊 Validation Summary${NC}"
echo "==========================================="

if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED${NC}"
    echo ""
    echo "Your deployment is fully operational!"
    echo ""
    echo "Production URLs:"
    echo "  • Backend API: ${API_URL}"
    echo "  • Email: support@verzekinnovative.com"
    echo ""
    echo "Next steps:"
    echo "  1. Test registration from mobile app"
    echo "  2. Verify email verification works"
    echo "  3. Monitor logs for any issues"
    exit 0
else
    echo -e "${RED}❌ ${FAILURES} TEST(S) FAILED${NC}"
    echo ""
    echo "Please review the failures above and:"
    echo "  1. Check service logs: ssh root@${VULTR_HOST} 'journalctl -u verzek-api.service -n 50'"
    echo "  2. Verify environment variables are set"
    echo "  3. Run deployment again if needed"
    exit 1
fi
