# Robot d’Assistance Autonome — RAA

Monorepo final du MVP RAA : site opérateur, API, WebSocket temps réel et workspace robot ROS 2.

## Objectif MVP

RAA automatise une mission logistique simple : créer une mission depuis le dashboard, l’envoyer au robot, naviguer vers le point A, scanner un QR code, prendre l’objet, naviguer vers le point B, déposer l’objet, puis clôturer la mission.

Workflow final :

```text
CREATED → ASSIGNED → NAVIGATING_TO_PICKUP → SCANNING_QR → PICKING_UP → NAVIGATING_TO_DROP → DROPPING_OFF → COMPLETED
                                                 ↘ ERROR à tout moment
```

## Architecture

```text
apps/web/              Image Nginx + build React
frontend/              Application React + TypeScript
apps/server/           API REST PHP 8.2 + MySQL
apps/server/realtime/  Serveur WebSocket Python
apps/robot/            Workspace ROS 2 Humble, Nav2, SLAM, QR, bras
packages/shared/       Réservé aux types partagés
.github/workflows/     CI/CD final
```

## Lancement local complet

Prérequis : Docker + Docker Compose.

```bash
docker compose -f docker-compose.realtime.yml up --build -d
```

Services :

- Dashboard web : http://localhost:8080
- API : http://localhost:8000/health
- WebSocket : ws://localhost:8765

Arrêt :

```bash
docker compose -f docker-compose.realtime.yml down -v
```

## Tests locaux comme la CI

```bash
./scripts/run_ci_local.sh
```

ou sous Windows PowerShell :

```powershell
.\scripts\run_ci_local.ps1
```

Les tests couvrent :

- santé API ;
- création/lecture missions ;
- workflow complet de statuts ;
- rejet des transitions invalides ;
- présence des points cartographiques ;
- service du front ;
- scénario WebSocket dashboard → robot → dashboard.

## Robot ROS 2

Le workspace ROS 2 est dans `apps/robot`.

Build image robot :

```bash
docker build -t raa-robot:humble apps/robot
```

Lancement mission MVP sur robot/Jetson après bringup Yahboom/Nav2 :

```bash
ros2 launch m3pro_teacher_vision mission_mvp.launch.py \
  api_base:=http://<IP_SERVEUR_API>:8000 \
  ws_url:=ws://<IP_SERVEUR_WS>:8765 \
  dry_run:=false \
  camera_topic:=/camera/color/image_raw/compressed
```

Pour répéter une démo sans mouvement réel :

```bash
ros2 launch m3pro_teacher_vision mission_mvp.launch.py dry_run:=true simulated_qr:=a
```

## CI/CD

La CI vérifie le serveur PHP, le front, les sources robot et le scénario d’intégration full stack.

La CD publie les images Docker suivantes dans GHCR :

- `api`
- `realtime`
- `web`
- `robot`

Sur `main`, si les secrets staging sont configurés, le déploiement met à jour le serveur avec `deploy/docker-compose.staging.yml`.

Secrets staging attendus :

- `STAGING_HOST`
- `STAGING_SSH_USER`
- `STAGING_SSH_KEY`
- `GHCR_TOKEN`

Optionnels :

- `STAGING_SSH_PORT`
- `STAGING_APP_DIR`
- `GHCR_USERNAME`
- variables GitHub `API_PORT`, `WEB_PORT`
