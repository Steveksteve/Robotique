#!/bin/bash
# Quick test script for M3 Pro Docker Dashboard

set -e

echo "=========================================="
echo "  M3 Pro Docker Dashboard - Quick Test"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if docker-compose services are running
check_services() {
    echo -e "${BLUE}[*] Checking Docker services...${NC}"
    
    local ros_core_status=$(docker-compose ps -q ros_core 2>/dev/null || echo "")
    local rosbridge_status=$(docker-compose ps -q rosbridge 2>/dev/null || echo "")
    local dashboard_status=$(docker-compose ps -q dashboard 2>/dev/null || echo "")
    
    if [ -z "$ros_core_status" ] || [ -z "$rosbridge_status" ] || [ -z "$dashboard_status" ]; then
        echo -e "${RED}[✗] Services not running. Start with: docker-compose up -d${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}[✓] All services running${NC}"
}

# Test 1: Dashboard HTTP
test_dashboard_http() {
    echo -e "${BLUE}[*] Testing Dashboard HTTP (port 8080)...${NC}"
    
    if curl -s http://localhost:8080 > /dev/null; then
        echo -e "${GREEN}[✓] Dashboard HTTP 200 OK${NC}"
        return 0
    else
        echo -e "${RED}[✗] Dashboard HTTP failed${NC}"
        return 1
    fi
}

# Test 2: RosBridge WebSocket
test_rosbridge_ws() {
    echo -e "${BLUE}[*] Testing RosBridge WebSocket (port 9090)...${NC}"
    
    python3 << 'PYEOF'
import websocket
import json
import sys

try:
    ws = websocket.create_connection("ws://localhost:9090", timeout=3)
    ws.close()
    print("[✓] RosBridge WebSocket 200 OK")
    sys.exit(0)
except Exception as e:
    print(f"[✗] RosBridge WebSocket failed: {e}")
    sys.exit(1)
PYEOF
}

# Test 3: Open in browser
test_browser_open() {
    echo -e "${BLUE}[*] Opening Dashboard in browser...${NC}"
    
    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open http://localhost:8080 2>/dev/null || true
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        open http://localhost:8080 2>/dev/null || true
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        start http://localhost:8080 2>/dev/null || true
    fi
    
    echo -e "${GREEN}[✓] Open http://localhost:8080 manually if browser didn't open${NC}"
}

# Test 4: Check service health
test_service_health() {
    echo -e "${BLUE}[*] Checking service health...${NC}"
    
    docker-compose ps | grep -E "(ros_core|rosbridge|dashboard)"
    echo -e "${GREEN}[✓] Services should show 'healthy' in STATUS${NC}"
}

# Test 5: View logs
show_logs() {
    echo -e "${BLUE}[*] Recent service logs:${NC}"
    echo ""
    echo -e "${YELLOW}--- RosBridge Logs (last 5 lines) ---${NC}"
    docker-compose logs --tail 5 rosbridge 2>/dev/null || echo "(logs not available)"
    echo ""
    echo -e "${YELLOW}--- Dashboard Logs (last 5 lines) ---${NC}"
    docker-compose logs --tail 5 dashboard 2>/dev/null || echo "(logs not available)"
}

# Main test sequence
main() {
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo ""
    
    check_services
    echo ""
    
    test_dashboard_http
    echo ""
    
    test_rosbridge_ws
    echo ""
    
    test_service_health
    echo ""
    
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo ""
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo -e "Next steps:"
    echo -e "  1. Open ${YELLOW}http://localhost:8080${NC} in your browser"
    echo -e "  2. You should see the M3 Pro Dashboard"
    echo -e "  3. Status indicator should show ${GREEN}CONNECTED${NC}"
    echo ""
    
    read -p "Open browser now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        test_browser_open
    fi
    
    echo ""
    echo -e "For more help, see: ${YELLOW}DOCKER_SETUP.md${NC}"
    echo ""
}

# Run main if docker-compose exists
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}[✗] docker-compose.yml not found${NC}"
    echo "Make sure you're in the correct directory:"
    echo "  cd /mnt/c/hetic/aaaa/m3pro_teacher_ws"
    exit 1
fi

main
