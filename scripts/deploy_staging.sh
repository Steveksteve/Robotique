#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/robotique}"
COMPOSE_FILE="$APP_DIR/docker-compose.staging.yml"
ENV_FILE="$APP_DIR/.env.staging"

required=(API_IMAGE REALTIME_IMAGE WEB_IMAGE GHCR_USERNAME GHCR_TOKEN)
for name in "${required[@]}"; do
  if [ -z "${!name:-}" ]; then
    echo "$name is required"
    exit 1
  fi
done

mkdir -p "$APP_DIR"

if [ ! -f "$ENV_FILE" ] && [ -f "$APP_DIR/.env.staging.example" ]; then
  cp "$APP_DIR/.env.staging.example" "$ENV_FILE"
fi

if [ ! -f "$COMPOSE_FILE" ]; then
  echo "Missing compose file: $COMPOSE_FILE"
  exit 1
fi

if [ ! -f "$APP_DIR/schema.sql" ]; then
  echo "Missing schema file: $APP_DIR/schema.sql"
  exit 1
fi

docker login ghcr.io -u "$GHCR_USERNAME" --password-stdin <<< "$GHCR_TOKEN"

export API_IMAGE REALTIME_IMAGE WEB_IMAGE
export API_PORT="${API_PORT:-8000}"
export WEB_PORT="${WEB_PORT:-8080}"

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" pull
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d --remove-orphans

for i in $(seq 1 45); do
  if curl -fsS "http://localhost:${API_PORT}/health" >/dev/null; then
    echo "Staging API is available"
    break
  fi
  sleep 2
  if [ "$i" -eq 45 ]; then
    echo "Deployment finished but API healthcheck did not pass in time"
    docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" logs --tail=150 api || true
    exit 1
  fi
done

for i in $(seq 1 45); do
  if curl -fsS "http://localhost:${WEB_PORT}/" >/dev/null; then
    echo "Staging web is available"
    exit 0
  fi
  sleep 2
  if [ "$i" -eq 45 ]; then
    echo "Deployment finished but web healthcheck did not pass in time"
    docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" logs --tail=150 web || true
    exit 1
  fi
done
