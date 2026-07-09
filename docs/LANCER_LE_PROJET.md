# Lancer le projet RAA

Ce guide explique comment demarrer le projet en local.

## Prerequis

- Docker
- Docker Compose

## Demarrage rapide

Depuis la racine du repo :

```bash
docker compose -f docker-compose.realtime.yml up --build -d
```

Cela lance :

- le dashboard web sur `http://localhost:8080`
- l API sur `http://localhost:8000/health`
- le serveur WebSocket sur `ws://localhost:8765`

## Verification

Tu peux verifier que tout repond bien avec :

```bash
curl http://localhost:8000/health
curl http://localhost:8080/
```

## Arret du projet

```bash
docker compose -f docker-compose.realtime.yml down -v
```

## Mode robot

Le workspace robot est dans `apps/robot`.

### Build de l image robot

```bash
docker build -t raa-robot:humble apps/robot
```

### Lancement de la mission MVP

```bash
ros2 launch m3pro_teacher_vision mission_mvp.launch.py \
  api_base:=http://<IP_SERVEUR_API>:8000 \
  ws_url:=ws://<IP_SERVEUR_WS>:8765 \
  dry_run:=false \
  camera_topic:=/camera/color/image_raw/compressed
```

### Demo sans mouvement reel

```bash
ros2 launch m3pro_teacher_vision mission_mvp.launch.py dry_run:=true simulated_qr:=a
```

## Aide pratique

Si tu veux lancer uniquement les services de test utilises par la CI, regarde aussi `docs/CI_LOCAL.md`.
