# Robot d’assistance autonome (RAA)

RAA est un prototype pédagogique de robot logistique. Un opérateur crée une mission depuis une interface web, l’affecte au robot et suit son avancement en temps réel.

Le dépôt regroupe le dashboard React, l’API PHP/MySQL, le serveur WebSocket et le workspace ROS 2 du robot.

## État actuel

Fonctionnel et testé :

- création, consultation et suppression des missions ;
- contrôle des transitions de statut ;
- synchronisation temps réel par WebSocket ;
- affichage de la position, des événements et des erreurs ;
- arrêt d’urgence logiciel et timeout de heartbeat ;
- mission complète avec le faux robot ;
- mission complète sur le robot en mode `dry_run` ;
- mission réelle de bout en bout : navigation, lecture du QR, prise, transport et dépose ;
- tests d’intégration de la stack web/API/WebSocket.

Contraintes d’utilisation actuelles : avant chaque démonstration, les nœuds ROS 2 nécessaires doivent être relancés et vérifiés. La valeur de fermeture de la pince doit également être ajustée selon l’objet afin d’obtenir une prise suffisante sans forcer sur le servomoteur. Ces points concernent la préparation et le calibrage du robot ; ils ne bloquent pas l’exécution complète de la mission. Le détail est dans [`docs/robot/ROBOT_FINAL_PIPELINE_STATUS.md`](docs/robot/ROBOT_FINAL_PIPELINE_STATUS.md).

## Parcours d’une mission

```text
CREATED
→ ASSIGNED
→ NAVIGATING_TO_PICKUP
→ SCANNING_QR
→ PICKING_UP
→ NAVIGATING_TO_DROP
→ DROPPING_OFF
→ COMPLETED
```

`ERROR` peut être atteint depuis tout état non terminal en cas d’erreur ou d’arrêt de sécurité.

La liste exacte des transitions se trouve dans [`docs/architecture/STATE_MACHINE.md`](docs/architecture/STATE_MACHINE.md).

## Organisation du dépôt

```text
frontend/              application React et TypeScript
apps/server/           API REST PHP 8.2, MySQL et serveur WebSocket Python
apps/robot/            packages ROS 2 Humble, navigation, vision et bras
packages/shared/       types et constantes partagés
tests/                 tests d’intégration et faux robot
.github/workflows/     CI et publication des images Docker
docs/                  documentation du projet
```

## Lancement local

Prérequis : Docker et Docker Compose.

```bash
docker compose -f docker-compose.realtime.yml up --build -d
```

Services :

- dashboard : `http://localhost:8080` ;
- API : `http://localhost:8000/health` ;
- WebSocket : `ws://localhost:8765`.

Pour arrêter et supprimer les volumes de test :

```bash
docker compose -f docker-compose.realtime.yml down -v
```

## Tester avec le faux robot

Après le lancement de la stack :

```bash
python -m pip install websockets
python tests/manual/fake_robot.py
```

Créer ensuite une mission dans le dashboard et l’affecter au robot `raa-fake-robot-01`.

## Développement du frontend

```bash
npm --prefix frontend ci
npm --prefix frontend run lint
npm --prefix frontend run build
npm --prefix frontend run dev
```

Le serveur Vite est disponible par défaut sur `http://localhost:5173`.

## Tests locaux

Sous Linux ou macOS :

```bash
./scripts/run_ci_local.sh
```

Sous Windows PowerShell :

```powershell
.\scripts\run_ci_local.ps1
```

Les tests vérifient notamment le workflow des missions, les transitions invalides, la persistance des logs, les points cartographiques, le frontend et les échanges WebSocket.

## Lancement de la mission ROS 2

Après le bringup du robot, Nav2 et le chargement des workspaces :

```bash
ros2 launch m3pro_teacher_vision mission_mvp.launch.py \
  api_base:=http://<IP_DU_PC>:8000 \
  ws_url:=ws://<IP_DU_PC>:8765 \
  robot_id:=raa-robot-01 \
  dry_run:=true \
  simulated_qr:=a
```

Le mode réel utilise `dry_run:=false`. Avant chaque essai, il faut relancer la chaîne de nœuds ROS 2, vérifier les services du bras et calibrer la fermeture de la pince. Les commandes détaillées et les vérifications de sécurité sont dans [`docs/robot/EXECUTION_GUIDE.md`](docs/robot/EXECUTION_GUIDE.md).

## Documentation

- [`docs/architecture/STATE_MACHINE.md`](docs/architecture/STATE_MACHINE.md) : états et transitions des missions ;
- [`docs/architecture/WEBSOCKET.md`](docs/architecture/WEBSOCKET.md) : messages temps réel utilisés ;
- [`docs/architecture/PIPELINE.md`](docs/architecture/PIPELINE.md) : contrôles CI et publication Docker ;
- [`docs/robot/EXECUTION_GUIDE.md`](docs/robot/EXECUTION_GUIDE.md) : lancement sur PC et sur le robot ;
- [`docs/robot/ROBOT_FINAL_PIPELINE_STATUS.md`](docs/robot/ROBOT_FINAL_PIPELINE_STATUS.md) : résultat réel des derniers essais ;
- [`docs/gestion-projet/Backlog.md`](docs/gestion-projet/Backlog.md) : tâches et état d’avancement ;
- [`docs/gestion-projet/ROADMAP.md`](docs/gestion-projet/ROADMAP.md) : déroulement du projet par étapes ;
- [`docs/qualite/ETHIQUE_RGPD_IA.md`](docs/qualite/ETHIQUE_RGPD_IA.md) : données, limites de sécurité et usage de l’IA ;
- [`docs/uml/diagrammes-uml-RAA.md`](docs/uml/diagrammes-uml-RAA.md) : diagrammes du MVP.
