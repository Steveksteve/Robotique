#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="docker-compose.test.yml"

echo "Building & starting services..."
docker compose -f "$COMPOSE_FILE" up --build -d

echo "Waiting for API at http://localhost:8000/ ..."
for i in $(seq 1 60); do
  if curl -sSf http://localhost:8000/ >/dev/null; then
    echo "API available"
    break
  fi
  sleep 1
done

echo "Installing test deps (if needed)..."
python -m pip install --upgrade pip || true
python -m pip install -r tests/integration/requirements-test.txt || true

echo "Running integration tests..."
mkdir -p reports || true
python -m pytest tests/integration/ -q --junitxml=reports/junit.xml
EXIT_CODE=$?

echo "Tearing down..."
docker compose -f "$COMPOSE_FILE" down -v

exit $EXIT_CODE
