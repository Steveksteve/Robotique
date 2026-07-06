# Merge Notes

Date: 2026-07-06

## Methode de fusion

Les trois dossiers fournis ne contenaient pas de repertoire `.git`. La conservation de l'historique via `git subtree`, `git merge --allow-unrelated-histories` ou branche distante n'etait donc pas possible depuis l'etat local.

La fusion a ete faite manuellement dans `Robotique-monorepo`, avec `Robotique-main` comme squelette applicatif et `Robotique-iot-scan-qr-code/Robotique-IOT-MVP/m3pro_teacher_ws` comme workspace ROS2 principal, car cette branche contient les ajouts QR/MVP en plus du code robotique de base.

Les dossiers generes ROS2 `build/`, `install/`, `log/`, les caches `__pycache__` et les fichiers `.DS_Store` n'ont pas ete copies dans le monorepo final. Aucune fonctionnalite source n'a ete supprimee.

## Structure analysee avant modification

### Robotique-IOT

Role fonctionnel:
- Workspace ROS2 Yahboom M3 Pro centre sur SLAM, Nav2, dashboard ROSBridge, vision, pick-and-place et controle du bras.

Dependances principales:
- ROS2 Humble, `rclpy`, `sensor_msgs`, `geometry_msgs`, `std_msgs`, `tf2_ros`, `nav2`, `slam_toolbox`, `rosbridge_server`, `cv_bridge`, OpenCV, `arm_msgs`.
- Docker ROS2 via `Dockerfile` et `docker-compose.yml`.

Points d'entree:
- `ros/m3pro_teacher_ws/docker-compose.yml` apres fusion.
- Launch ROS2: `live_showcase.launch.py`, `sim_showcase.launch.py`, `navigation.launch.py`, `slam_and_nav.launch.py`, `slam_online.launch.py`, `detect_and_pick.launch.py`, `web_dashboard.launch.py`.
- Nodes: `arm_manual_control_node`, `arm_joint_state_bridge_demo`, `object_detector_node`, `pick_and_place_node`, `camera_obstacle_node`, `web_server_node`.

Differences:
- Contient le flux detection/pick-and-place original.
- Ne contient pas le node QR ni l'executeur de mission MVP.

### Robotique-iot-scan-qr-code

Role fonctionnel:
- Variante MVP du workspace ROS2 avec lecture QR et execution de mission connectee a l'API web.

Dependances principales:
- Memes dependances ROS2 que `Robotique-IOT`.
- Ajouts QR: `pyzbar`, OpenCV, NumPy, `std_srvs`.
- Ajouts mission: `nav2_msgs`, `m3pro_teacher_interfaces`.

Points d'entree:
- `qr_code_reader_node`
- `mission_executor_node`
- `mission_mvp.launch.py`

Differences:
- Ajoute `src/m3pro_teacher_vision/m3pro_teacher_vision/qr_code_reader_node.py`.
- Ajoute `src/m3pro_teacher_vision/m3pro_teacher_vision/mission_executor_node.py`.
- Ajoute `src/m3pro_teacher_vision/launch/mission_mvp.launch.py`.
- Ajoute les cartes `salle.pgm` et `salle.yaml`.
- Contenait des artefacts generes `build/`, `install/`, `log/` exclus de la fusion source.

### Robotique-main

Role fonctionnel:
- Monorepo applicatif RAA: API missions, dashboard React, WebSocket, client robot simule, CI et tests.

Dependances principales:
- Frontend: React, TypeScript, Vite.
- API: PHP, MySQL.
- Temps reel: Python WebSocket.
- Tests: pytest, requests/websocket selon `tests/integration/requirements-test.txt`.

Points d'entree:
- API: `apps/server/public/index.php`
- Realtime: `apps/server/realtime/ws_server.py`
- Frontend: `frontend/src/main.tsx`
- Compose: `docker-compose.realtime.yml`, `docker-compose.test.yml`
- Robot simule: `apps/robot/client.py`

Differences:
- Contient le socle API/web/tests mais pas le workspace ROS2 complet.
- Les statuts missions initiaux ne couvraient pas tout le workflow QR du node ROS2.

## Code bras robotique repere

Fichiers conserves sous `ros/m3pro_teacher_ws`:
- `src/m3pro_teacher_demos/m3pro_teacher_demos/arm_manual_control_node.py`
- `src/m3pro_teacher_demos/m3pro_teacher_demos/arm_joint_state_bridge_demo.py`
- `src/m3pro_teacher_demos/scripts/arm_control_cli.py`
- `src/m3pro_teacher_vision/m3pro_teacher_vision/pick_and_place_node.py`
- `src/m3pro_teacher_interfaces/srv/Home.srv`
- `src/m3pro_teacher_interfaces/srv/SetJoint.srv`
- `src/m3pro_teacher_interfaces/srv/SetJoints.srv`
- `ARM_MANUAL_CONTROL.md`
- `docs/legacy/bras.md`

Aucun fichier `Rosmaster_Lib.py` n'a ete trouve dans les trois dossiers locaux.

## Code QR repere

Fichiers conserves sous `ros/m3pro_teacher_ws`:
- `src/m3pro_teacher_vision/m3pro_teacher_vision/qr_code_reader_node.py`
- `src/m3pro_teacher_vision/m3pro_teacher_vision/mission_executor_node.py`
- `src/m3pro_teacher_vision/launch/mission_mvp.launch.py`
- Entrees `console_scripts` correspondantes dans `src/m3pro_teacher_vision/setup.py`.

Le node QR expose:
- Topic lu: `camera_topic`, par defaut `/camera/color/image_raw/compressed`.
- Topic publie: `/qr_code`.
- Service: `/qr/read`.

## Doublons et conflits traites

### Workspace ROS2

`Robotique-IOT` et `Robotique-iot-scan-qr-code` etaient presque identiques. La branche QR a ete prise comme base ROS2, puis les conflits ont ete resolus.

Conflit important:
- `detect_and_pick.launch.py` avait ete remplace dans la branche QR par un lancement QR/mission.
- Decision: restaurer `detect_and_pick.launch.py` pour detection/pick-and-place, et garder le flux QR dans `mission_mvp.launch.py`.

### API missions

Conflit important:
- `mission_executor_node.py` emet les statuts `SCANNING_QR` et `DROPPING_OFF`.
- `Robotique-main/apps/server/src/MissionController.php` et `schema.sql` ne les acceptaient pas.
- Decision: ajouter ces deux statuts et transitions cote API et schema SQL.

### Dependances QR

Conflit important:
- `qr_code_reader_node.py` utilise `pyzbar`, OpenCV et NumPy.
- Le Dockerfile ROS2 n'installait pas explicitement `pyzbar`/`zbar`.
- Decision: ajouter `python3-pyzbar`, `libzbar0`, `python3-numpy` au Dockerfile ROS2, et documenter les dependances dans `package.xml`.

### Configs Docker

Les compose applicatifs de `Robotique-main` sont conserves a la racine:
- `docker-compose.realtime.yml`
- `docker-compose.test.yml`
- `deploy/docker-compose.staging.yml`

Le compose ROS2 est conserve dans:
- `ros/m3pro_teacher_ws/docker-compose.yml`

Ils ne sont pas fusionnes en un seul fichier global car ils orchestrent des environnements differents: API/web/realtime d'un cote, ROS2/rosbridge/dashboard embarque de l'autre.

## Arborescence cible

```text
Robotique-monorepo/
  apps/
    robot/
    server/
    websocket/
  deploy/
  docs/
    legacy/
    uml/
  frontend/
  packages/
    shared/
  ros/
    m3pro_teacher_ws/
      src/
        m3pro_teacher_demos/
        m3pro_teacher_description/
        m3pro_teacher_interfaces/
        m3pro_teacher_nav/
        m3pro_teacher_vision/
        m3pro_teacher_web/
  scripts/
  tests/
  MERGE_NOTES.md
  README.md
```

## Verification effectuee

Commandes lancees:

- Parsing syntaxique Python via `ast.parse` sur les fichiers `.py` du monorepo: 34 fichiers verifies, aucun `SyntaxError`.
- `php -l apps/server/src/MissionController.php`: aucun probleme de syntaxe.
- Parsing XML de tous les `package.xml` ROS2: 6 manifests valides.
- Parsing JSON de tous les `package.json`: 2 fichiers valides.
- Verification de presence des fichiers critiques:
  - `ros/m3pro_teacher_ws/src/m3pro_teacher_vision/m3pro_teacher_vision/qr_code_reader_node.py`
  - `ros/m3pro_teacher_ws/src/m3pro_teacher_vision/m3pro_teacher_vision/mission_executor_node.py`
  - `ros/m3pro_teacher_ws/src/m3pro_teacher_demos/m3pro_teacher_demos/arm_manual_control_node.py`
  - `ros/m3pro_teacher_ws/src/m3pro_teacher_nav/maps/salle.yaml`
- Verification que les dossiers ROS2 generes `build/`, `install/`, `log/` et `__pycache__` n'ont pas ete copies sous `ros/m3pro_teacher_ws`.
- Verification de coherence des statuts `SCANNING_QR` et `DROPPING_OFF` entre `mission_executor_node.py`, `MissionController.php` et `schema.sql`.

Non execute:

- Build ROS2 `colcon build`, car il depend d'un environnement ROS2 Humble complet et des packages materiels Yahboom comme `arm_msgs`.
- Tests Docker/API et frontend, car ils peuvent necessiter Docker, dependances installees et services locaux.

## Points de vigilance restants

- Le build ROS2 complet necessite une image/environnement ROS2 Humble avec les packages Yahboom, notamment `arm_msgs`.
- Les tests Docker/API peuvent necessiter Docker et un acces reseau local.
- L'historique Git pourra etre preserve ulterieurement seulement si les remotes ou clones Git originaux sont fournis.
