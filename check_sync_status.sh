#!/bin/bash
# VerzekAutoTrader - GitHub Sync Status Checker
# Checks if Replit code is in sync with GitHub
#
# Usage:
#   chmod +x check_sync_status.sh
#   ./check_sync_status.sh

set -e

echo "🔍 VerzekAutoTrader - GitHub Sync Status Check"
echo "=============================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check backend
echo -e "${BLUE}📦 Backend Repository Status:${NC}"
echo "Repository: https://github.com/ellizza78/VerzekBackend"
cd backend 2>/dev/null || cd ~/workspace/backend 2>/dev/null || {
    echo -e "${RED}❌ Backend directory not found${NC}"
    exit 1
}

echo ""
echo -e "${YELLOW}Current branch:${NC}"
git branch -v | grep '^\*'

echo ""
echo -e "${YELLOW}Remote status:${NC}"
git remote -v | grep origin | head -1

echo ""
echo -e "${YELLOW}Commits ahead/behind:${NC}"
git status -sb

echo ""
echo -e "${YELLOW}Uncommitted changes:${NC}"
if git diff --quiet && git diff --cached --quiet; then
    echo -e "${GREEN}✅ No uncommitted changes${NC}"
else
    echo -e "${RED}⚠️  Uncommitted changes detected:${NC}"
    git status --short
fi

echo ""
echo -e "${YELLOW}Latest commit:${NC}"
git log -1 --oneline

# Check if ahead of remote
AHEAD=$(git rev-list origin/main..HEAD --count 2>/dev/null || echo "0")
BEHIND=$(git rev-list HEAD..origin/main --count 2>/dev/null || echo "0")

echo ""
if [ "$AHEAD" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Backend is ${AHEAD} commit(s) ahead of GitHub${NC}"
    echo "   Run: git push origin main"
elif [ "$BEHIND" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Backend is ${BEHIND} commit(s) behind GitHub${NC}"
    echo "   Run: git pull origin main"
else
    echo -e "${GREEN}✅ Backend is in sync with GitHub${NC}"
fi

# Check frontend
echo ""
echo "=============================================="
echo -e "${BLUE}📱 Frontend Repository Status:${NC}"
echo "Repository: https://github.com/ellizza78/VerzekAutoTrader"
cd ../mobile_app/VerzekApp 2>/dev/null || cd ~/workspace/mobile_app/VerzekApp 2>/dev/null || {
    echo -e "${RED}❌ Frontend directory not found${NC}"
    exit 1
}

echo ""
echo -e "${YELLOW}Current branch:${NC}"
git branch -v | grep '^\*'

echo ""
echo -e "${YELLOW}Remote status:${NC}"
git remote -v | grep origin | head -1

echo ""
echo -e "${YELLOW}Commits ahead/behind:${NC}"
git status -sb

echo ""
echo -e "${YELLOW}Uncommitted changes:${NC}"
if git diff --quiet && git diff --cached --quiet; then
    echo -e "${GREEN}✅ No uncommitted changes${NC}"
else
    echo -e "${RED}⚠️  Uncommitted changes detected:${NC}"
    git status --short
fi

echo ""
echo -e "${YELLOW}Latest commit:${NC}"
git log -1 --oneline

# Check if ahead of remote
AHEAD=$(git rev-list origin/main..HEAD --count 2>/dev/null || echo "0")
BEHIND=$(git rev-list HEAD..origin/main --count 2>/dev/null || echo "0")

echo ""
if [ "$AHEAD" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Frontend is ${AHEAD} commit(s) ahead of GitHub${NC}"
    echo "   Run: git push origin main"
elif [ "$BEHIND" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Frontend is ${BEHIND} commit(s) behind GitHub${NC}"
    echo "   Run: git pull origin main"
else
    echo -e "${GREEN}✅ Frontend is in sync with GitHub${NC}"
fi

# Verify critical files
echo ""
echo "=============================================="
echo -e "${BLUE}🔍 Critical Files Verification:${NC}"
echo ""

# Backend critical files
echo -e "${YELLOW}Backend Files:${NC}"
cd ../../backend 2>/dev/null || cd ~/workspace/backend
[ -f "requirements.txt" ] && echo -e "  ${GREEN}✅${NC} requirements.txt" || echo -e "  ${RED}❌${NC} requirements.txt"
[ -f "api_server.py" ] && echo -e "  ${GREEN}✅${NC} api_server.py" || echo -e "  ${RED}❌${NC} api_server.py"
[ -f "auth_routes.py" ] && echo -e "  ${GREEN}✅${NC} auth_routes.py" || echo -e "  ${RED}❌${NC} auth_routes.py"
[ -f "utils/email.py" ] && echo -e "  ${GREEN}✅${NC} utils/email.py" || echo -e "  ${RED}❌${NC} utils/email.py"
[ -f "models.py" ] && echo -e "  ${GREEN}✅${NC} models.py" || echo -e "  ${RED}❌${NC} models.py"

# Check resend version
if grep -q "resend==2.19.0" requirements.txt; then
    echo -e "  ${GREEN}✅${NC} resend==2.19.0 (correct version)"
else
    echo -e "  ${RED}❌${NC} resend version incorrect (should be 2.19.0)"
fi

echo ""
echo -e "${YELLOW}Frontend Files:${NC}"
cd ../mobile_app/VerzekApp 2>/dev/null || cd ~/workspace/mobile_app/VerzekApp
[ -f "app.json" ] && echo -e "  ${GREEN}✅${NC} app.json" || echo -e "  ${RED}❌${NC} app.json"
[ -f "src/config/api.js" ] && echo -e "  ${GREEN}✅${NC} src/config/api.js" || echo -e "  ${RED}❌${NC} src/config/api.js"
[ -f "src/screens/LoginScreen.js" ] && echo -e "  ${GREEN}✅${NC} src/screens/LoginScreen.js" || echo -e "  ${RED}❌${NC} src/screens/LoginScreen.js"

# Check API URL
if grep -q "https://api.verzekinnovative.com" src/config/api.js; then
    echo -e "  ${GREEN}✅${NC} API URL correct (https://api.verzekinnovative.com)"
else
    echo -e "  ${RED}❌${NC} API URL incorrect"
fi

echo ""
echo "=============================================="
echo -e "${GREEN}✅ Sync status check complete!${NC}"
echo ""
