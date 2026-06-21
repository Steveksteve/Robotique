#!/bin/bash
# Start Docker services for M3 Pro Teacher Workspace

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$SCRIPT_DIR"

echo "=================================================="
echo "  M3 Pro Teacher Workspace - Docker Launcher"
echo "=================================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ensure docker-compose is available
if ! command -v docker-compose &> /dev/null && ! command -v docker compose &> /dev/null; then
    echo -e "${RED}✗ docker-compose not found${NC}"
    exit 1
fi

# Use 'docker compose' or 'docker-compose' based on availability
if command -v docker compose &> /dev/null; then
    DC="docker compose"
else
    DC="docker-compose"
fi

cd "$PROJECT_DIR"

# Function to print usage
usage() {
    cat << EOF
Usage: $0 [COMMAND] [OPTIONS]

Commands:
  build           Build the Docker image
  up              Start all services (with build)
  up-no-build     Start all services (without rebuild)
  down            Stop all services
  logs            Show logs from all services
  logs [SERVICE]  Show logs from specific service (ros_core, rosbridge, dashboard)
  status          Show status of all services
  shell [SERVICE] Enter shell in a service
  test-bridge     Test RosBridge connection
  test-dashboard  Test Dashboard HTTP connection
  clean           Remove stopped containers and volumes
  help            Show this help message

Examples:
  $0 build
  $0 up
  $0 logs rosbridge
  $0 shell ros_core
  $0 test-bridge
  $0 down

EOF
}

# Function to build
build_image() {
    echo -e "${BLUE}[*] Building Docker image...${NC}"
    $DC build
    echo -e "${GREEN}[✓] Build complete${NC}"
}

# Function to start services
start_services() {
    echo -e "${BLUE}[*] Starting Docker services...${NC}"
    $DC up -d
    sleep 2
    echo -e "${GREEN}[✓] Services started${NC}"
    echo ""
    status_services
}

# Function to start services without build
start_services_no_build() {
    echo -e "${BLUE}[*] Starting Docker services (no rebuild)...${NC}"
    $DC up -d --no-build
    sleep 2
    echo -e "${GREEN}[✓] Services started${NC}"
    echo ""
    status_services
}

# Function to stop services
stop_services() {
    echo -e "${BLUE}[*] Stopping Docker services...${NC}"
    $DC down
    echo -e "${GREEN}[✓] Services stopped${NC}"
}

# Function to show status
status_services() {
    echo -e "${BLUE}[*] Service Status:${NC}"
    $DC ps
    echo ""
    echo -e "${YELLOW}📊 Dashboard Access:${NC}"
    echo "  • Web: ${GREEN}http://localhost:8080${NC}"
    echo "  • RosBridge WebSocket: ${GREEN}ws://localhost:9090${NC}"
}

# Function to show logs
show_logs() {
    if [ -z "$1" ]; then
        echo -e "${BLUE}[*] Showing logs from all services (Ctrl+C to exit)...${NC}"
        $DC logs -f
    else
        echo -e "${BLUE}[*] Showing logs from service: $1 (Ctrl+C to exit)...${NC}"
        $DC logs -f "$1"
    fi
}

# Function to enter shell
enter_shell() {
    local SERVICE=${1:-ros_core}
    echo -e "${BLUE}[*] Entering shell in $SERVICE...${NC}"
    $DC exec "$SERVICE" bash
}

# Function to test RosBridge
test_rosbridge() {
    echo -e "${BLUE}[*] Testing RosBridge connection...${NC}"
    python3 << 'PYEOF'
import websocket
import json
import sys

try:
    print("[...] Connecting to ws://localhost:9090...")
    ws = websocket.create_connection("ws://localhost:9090", timeout=5)
    print("[✓] Connected!")
    
    # Test basic command
    ws.send(json.dumps({"op": "call_service", "service": "/rosapi/services"}))
    result = ws.recv()
    
    print("[✓] RosBridge is working!")
    print(f"[✓] Response: {result[:100]}...")
    ws.close()
    sys.exit(0)
except Exception as e:
    print(f"[✗] RosBridge error: {e}")
    print("[!] Make sure services are running: docker-compose up -d")
    sys.exit(1)
PYEOF
}

# Function to test Dashboard
test_dashboard() {
    echo -e "${BLUE}[*] Testing Dashboard HTTP connection...${NC}"
    python3 << 'PYEOF'
import urllib.request
import sys

try:
    print("[...] Connecting to http://localhost:8080...")
    response = urllib.request.urlopen("http://localhost:8080", timeout=5)
    print("[✓] Dashboard is running!")
    print(f"[✓] HTTP Status: {response.status}")
    sys.exit(0)
except Exception as e:
    print(f"[✗] Dashboard error: {e}")
    print("[!] Make sure services are running: docker-compose up -d")
    sys.exit(1)
PYEOF
}

# Function to clean up
clean_resources() {
    echo -e "${YELLOW}[!] This will remove stopped containers and volumes${NC}"
    read -p "Continue? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}[*] Cleaning up...${NC}"
        $DC down -v
        docker volume prune -f
        echo -e "${GREEN}[✓] Cleanup complete${NC}"
    else
        echo "Cancelled."
    fi
}

# Main command handling
case "${1:-help}" in
    build)
        build_image
        ;;
    up)
        build_image
        start_services
        ;;
    up-no-build|up-nb)
        start_services_no_build
        ;;
    down|stop)
        stop_services
        ;;
    logs)
        show_logs "$2"
        ;;
    status|ps)
        status_services
        ;;
    shell|sh)
        enter_shell "$2"
        ;;
    test-bridge|test-rosbridge)
        test_rosbridge
        ;;
    test-dashboard)
        test_dashboard
        ;;
    clean|cleanup)
        clean_resources
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo ""
        usage
        exit 1
        ;;
esac

echo ""
