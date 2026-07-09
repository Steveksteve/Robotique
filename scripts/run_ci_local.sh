#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="docker-compose.test.yml"
API_BASE="${API_BASE:-http://localhost:8000}"
WS_URL="${WS_URL:-ws://localhost:8765}"
WEB_BASE="${WEB_BASE:-http://localhost:8080}"

cleanup() {
  docker compose -f "$COMPOSE_FILE" down -v || true
}
trap cleanup EXIT

docker compose -f "$COMPOSE_FILE" up --build -d

for i in $(seq 1 90); do
  if curl -fsS "$API_BASE/health" >/dev/null; then
    echo "API ready"
    break
  fi
  sleep 1
  if [ "$i" -eq 90 ]; then
    docker compose -f "$COMPOSE_FILE" logs api
    exit 1
  fi
done

for i in $(seq 1 90); do
  if curl -fsS "$WEB_BASE/" >/dev/null; then
    echo "Web ready"
    break
  fi
  sleep 1
  if [ "$i" -eq 90 ]; then
    docker compose -f "$COMPOSE_FILE" logs web
    exit 1
  fi
done

python -m pip install -r tests/integration/requirements-test.txt
mkdir -p reports
python -m pytest tests/unit/iot -q --junitxml=reports/junit-unit.xml
API_BASE="$API_BASE" WS_URL="$WS_URL" WEB_BASE="$WEB_BASE" \
  python -m pytest tests/integration/ -q --junitxml=reports/junit.xml
