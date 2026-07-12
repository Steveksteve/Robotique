# Robot d’Assistance Autonome — RAA

Monorepo du MVP RAA : interface opérateur, API REST, serveur WebSocket temps réel et workspace robot ROS 2.

## Objectif du MVP

RAA automatise une mission logistique simple : création d’une mission depuis le dashboard, affectation au robot, navigation vers le point de prise, lecture d’un QR code, prise de l’objet, navigation vers le point de dépôt, dépose de l’objet et clôture de la mission.

## Machine à états de référence

La machine à états ci-dessous est la référence commune au frontend, à l’API, au serveur WebSocket, au robot et à la documentation.

```text
CREATED
-> ASSIGNED
-> NAVIGATING_TO_PICKUP
-> SCANNING_QR
-> PICKING_UP
-> NAVIGATING_TO_DROP
-> DROPPING_OFF
-> COMPLETED
```

`ERROR` est l’unique état terminal d’échec. Il peut être atteint depuis n’importe quel état non terminal. Un arrêt d’urgence, une perte de heartbeat, une erreur de navigation, un QR incorrect ou une erreur du bras entraînent donc un passage à `ERROR`.

Aucun autre état terminal n’est persisté dans le MVP.

La définition détaillée des transitions se trouve dans [`docs/architecture/STATE_MACHINE.md`](docs/architecture/STATE_MACHINE.md). Les diagrammes correspondants se trouvent dans [`docs/uml/diagrammes-uml-RAA.md`](docs/uml/diagrammes-uml-RAA.md).

## Architecture

```text
apps/web/              Image Nginx et build React
frontend/              Application React et TypeScript
apps/server/           API REST PHP 8.2 et MySQL
apps/server/realtime/  Serveur WebSocket Python
apps/robot/            Workspace ROS 2 Humble, Nav2, SLAM, QR et bras
packages/shared/       Types et constantes partagés
.github/workflows/     Workflows CI/CD
```

## Lancement local complet

Prérequis : Docker et Docker Compose.

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

## Développement du frontend

```bash
npm --prefix frontend ci
npm run web:build
npm run web:lint
npm run web:dev
```

Le serveur de développement est disponible par défaut sur http://localhost:5173.

## Tests locaux équivalents à la CI

```bash
./scripts/run_ci_local.sh
```

Sous Windows PowerShell :

```powershell
.\scripts\run_ci_local.ps1
```

Les tests couvrent :

- la santé de l’API ;
- la création et la lecture des missions ;
- le workflow complet des statuts ;
- le rejet des transitions invalides ;
- la persistance des logs robot ;
- la présence des points cartographiques ;
- le service du frontend ;
- le scénario WebSocket dashboard vers robot puis robot vers dashboard.

## Robot ROS 2

Le workspace ROS 2 se trouve dans `apps/robot`.

Construction de l’image robot :

```bash
docker build -t raa-robot:humble apps/robot
```

Lancement de la mission MVP sur le robot ou la Jetson après le bringup Yahboom et Nav2 :

```bash
ros2 launch m3pro_teacher_vision mission_mvp.launch.py \
api_base:=http://<IP_SERVEUR_API>:8000 \
ws_url:=ws://<IP_SERVEUR_WS>:8765 \
dry_run:=false \
camera_topic:=/camera/color/image_raw/compressed
```

Pour répéter une démonstration sans mouvement réel :

```bash
ros2 launch m3pro_teacher_vision mission_mvp.launch.py dry_run:=true simulated_qr:=a
```

L’état réel des essais, y compris la limite actuelle liée au flux caméra et à la lecture QR, est documenté dans [`docs/robot/ROBOT_FINAL_PIPELINE_STATUS.md`](docs/robot/ROBOT_FINAL_PIPELINE_STATUS.md).

## CI/CD

La CI vérifie le serveur PHP, le frontend, les sources robot et le scénario d’intégration full stack.

La CD publie les images Docker suivantes dans GHCR :

- `api`
- `realtime`
- `web`
- `robot`

Sur `main`, si les secrets de staging sont configurés, le déploiement met à jour le serveur avec `deploy/docker-compose.staging.yml`.

Secrets de staging attendus :

- `STAGING_HOST`
- `STAGING_SSH_USER`
- `STAGING_SSH_KEY`
- `GHCR_TOKEN`

Paramètres optionnels :

- `STAGING_SSH_PORT`
- `STAGING_APP_DIR`
- `GHCR_USERNAME`
- variables GitHub `API_PORT` et `WEB_PORT`

## Éthique, RGPD et usage de l’IA

La politique du projet concernant les données techniques, la durée de conservation, la sécurité et l’usage déclaré d’outils d’intelligence artificielle est décrite dans [`docs/qualite/ETHIQUE_RGPD_IA.md`](docs/qualite/ETHIQUE_RGPD_IA.md).

## Documentation principale

- [`docs/architecture/STATE_MACHINE.md`](docs/architecture/STATE_MACHINE.md) : machine à états de référence
- [`docs/uml/diagrammes-uml-RAA.md`](docs/uml/diagrammes-uml-RAA.md) : diagrammes UML
- [`docs/architecture/PIPELINE.md`](docs/architecture/PIPELINE.md) : pipeline CI/CD
- [`docs/architecture/WEBSOCKET.md`](docs/architecture/WEBSOCKET.md) : protocole temps réel
- [`docs/qualite/ETHIQUE_RGPD_IA.md`](docs/qualite/ETHIQUE_RGPD_IA.md) : éthique, RGPD et usage de l’IA
- [`docs/robot/ROBOT_FINAL_PIPELINE_STATUS.md`](docs/robot/ROBOT_FINAL_PIPELINE_STATUS.md) : état réel des essais robot
