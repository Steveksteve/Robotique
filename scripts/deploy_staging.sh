#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/robotique}"
COMPOSE_FILE="$APP_DIR/docker-compose.staging.yml"
ENV_FILE="$APP_DIR/.env.staging"

if [ -z "${API_IMAGE:-}" ]; then
  echo "API_IMAGE is required"
  exit 1
fi

if [ -z "${GHCR_USERNAME:-}" ] || [ -z "${GHCR_TOKEN:-}" ]; then
  echo "GHCR credentials are required"
  exit 1
fi

mkdir -p "$APP_DIR"

if [ ! -f "$ENV_FILE" ] && [ -f "$APP_DIR/.env.staging.example" ]; then
  cp "$APP_DIR/.env.staging.example" "$ENV_FILE"
fi

docker login ghcr.io -u "$GHCR_USERNAME" --password-stdin <<< "$GHCR_TOKEN"

export API_IMAGE
export API_PORT="${API_PORT:-8000}"

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" pull
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d

for i in $(seq 1 30); do
  if curl -fsS "http://localhost:${API_PORT}/" >/dev/null; then
    echo "Staging API is available"
    exit 0
  fi
  sleep 2
done

echo "Deployment finished but API healthcheck did not pass in time"
exit 1
