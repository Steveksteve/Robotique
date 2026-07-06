# Robotique Monorepo

Monorepo fusionne pour le Robot d'Assistance Autonome.

## Structure

```text
apps/server              API PHP/MySQL missions
apps/server/realtime     Serveur WebSocket temps reel
apps/robot               Client robot/simulation API
frontend                 Dashboard React/Vite
ros/m3pro_teacher_ws     Workspace ROS2 Yahboom M3 Pro
tests                    Tests integration et outils manuels
docs                     Documentation projet
```

## Demarrage rapide

API, WebSocket et IoT ROS2:

```bash
docker compose up --build
```

Verifier uniquement l'image IoT:

```bash
docker compose --profile iot-build up --build iot_base
```

Lancer aussi l'executeur de mission QR:

```bash
docker compose --profile mission up --build
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Workspace ROS2:

```bash
cd ros/m3pro_teacher_ws
docker compose up --build
```

Flux mission QR ROS2:

```bash
cd ros/m3pro_teacher_ws
ros2 launch m3pro_teacher_vision mission_mvp.launch.py
```

Vision et pick-and-place ROS2:

```bash
cd ros/m3pro_teacher_ws
ros2 launch m3pro_teacher_vision detect_and_pick.launch.py
```

Les decisions et conflits de fusion sont documentes dans `MERGE_NOTES.md`.
