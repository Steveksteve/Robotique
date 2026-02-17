# RAA — Robot d'Assistance Autonome

> Robot mobile autonome qui transporte des objets d'un point A à un point B au sein d'un bâtiment, pour le personnel d'une bibliothèque municipale ou d'un centre administratif.

**HETIC Web3 — Février 2026**

---

## Sommaire

- [Vision du projet](#vision-du-projet)
- [Objectifs et périmètre](#objectifs-et-périmètre)
- [Architecture technique](#architecture-technique)
- [Stack technique](#stack-technique)
- [Structure du monorepo](#structure-du-monorepo)
- [API REST](#api-rest)
- [Events WebSocket](#events-websocket)
- [Machine à états — Mission](#machine-à-états--mission)
- [Packages ROS 2](#packages-ros-2)
- [Installation](#installation)
- [Branches Git](#branches-git)
- [Conventions équipe](#conventions-équipe)
- [Roadmap](#roadmap)
- [Risques et mitigations](#risques-et-mitigations)
- [Équipe](#équipe)

---

## Vision du projet

**RAA** (Robot d'Assistance Autonome) est un prototype MVP développé en **5 semaines** par une équipe de **5 étudiants HETIC**, construit sur du matériel grand public (**Yahboom Transbot** — Jetson Nano + Lidar + RealSense + Bras Robotique) et des logiciels open-source (**ROS 2 Humble**).

### Objectifs stratégiques

- Démontrer la faisabilité technique d'un robot autonome sur du matériel accessible (<500 euros)
- Valider l'intégration full-stack : interface web ↔ serveur ↔ robot en temps réel
- Produire un MVP documenté, maintenable et extensible pour les promotions suivantes
- Préparer une démo jury convaincante, fiable et répétable

---

## Objectifs et périmètre

### In Scope (MVP)

| # | Fonctionnalité | Priorité |
|---|----------------|----------|
| 1 | Navigation autonome point A → point B dans un environnement cartographié | Critique |
| 2 | Évitement d'obstacles statiques et dynamiques via Lidar | Critique |
| 3 | Pick-up et drop-off d'un objet standardisé via le bras robotique | Critique |
| 4 | Interface opérateur web pour créer et suivre les missions en temps réel | Critique |
| 5 | Mise à jour du statut de mission en temps réel (WebSocket) | Critique |
| 6 | Arrêt d'urgence physique et logiciel | Critique |
| 7 | Monitoring de la batterie avec seuil d'alerte | Important |
| 8 | Interface accessible WCAG AA (navigation clavier, lecteur d'écran) | Important |

### Out of Scope

- Navigation multi-étages ou ascenseur
- Reconnaissance visuelle d'objets
- Gestion de plusieurs robots simultanément
- Authentification utilisateur (mono-utilisateur pour le MVP)
- Déploiement en production ou en cloud
- Persistance longue durée / analytics des missions
- Application mobile native

---

## Architecture technique

```
┌──────────────────────────────────────────────────────────────┐
│                        NAVIGATEUR                             │
│   React 18 + TypeScript + Tailwind CSS + Socket.io-client     │
│   Dashboard missions · Carte SVG · Vue live · Notifications   │
└─────────────────────────┬────────────────────────────────────┘
                          │ WebSocket + REST
┌─────────────────────────▼────────────────────────────────────┐
│                     SERVEUR BACK-END                          │
│              PHP + MySQL + Socket.io                           │
│   API REST missions · Bridge WebSocket · Emergency stop       │
│                          │                                    │
│                    ┌─────▼─────┐                              │
│                    │   MySQL   │                               │
│                    └───────────┘                               │
└─────────────────────────┬────────────────────────────────────┘
                          │ WebSocket
┌─────────────────────────▼────────────────────────────────────┐
│                   ROBOT — Jetson Nano                          │
│                  ROS 2 Humble + Python                         │
│                                                               │
│   ┌───────────┐  ┌───────────┐  ┌───────────┐               │
│   │   Nav2    │  │   Lidar   │  │ RealSense │               │
│   │Navigation │  │  SLAM     │  │  (depth)  │               │
│   └───────────┘  └───────────┘  └───────────┘               │
│   ┌───────────┐  ┌────────────────┐  ┌────────────────┐     │
│   │   Bras    │  │ mission_manager│  │ safety_monitor │     │
│   │ robotique │  │   (custom)     │  │   (custom)     │     │
│   └───────────┘  └────────────────┘  └────────────────┘     │
└──────────────────────────────────────────────────────────────┘
```

Les trois couches sont **découplées** et communiquent par **API REST** et **WebSocket**, permettant à chaque sous-équipe de travailler en parallèle.

---

## Stack technique

### Front-end

| Technologie | Rôle |
|-------------|------|
| React 18 + TypeScript | Framework UI avec typage fort |
| Tailwind CSS | Développement rapide, cohérence visuelle |
| Socket.io-client | Temps réel avec reconnexion automatique |
| React Query | Cache intelligent, gestion loading/error |
| React Router v6 | Routing SPA |

### Back-end

| Technologie | Rôle |
|-------------|------|
| PHP | API REST, gestion des missions |
| MySQL | Base de données relationnelle |
| Socket.io | Rooms, broadcast, relay robot ↔ front |

### Robot (IoT)

| Technologie | Rôle |
|-------------|------|
| ROS 2 Humble | Middleware robotique (LTS) |
| Nav2 | Navigation autonome, planification, évitement obstacles |
| slam_toolbox | Cartographie SLAM via Lidar |
| robot_localization | Fusion odometry + IMU |
| Python 3 | Nodes custom (mission_manager, arm_controller, safety_monitor) |

### Matériel

| Composant | Spécification |
|-----------|---------------|
| Plateforme | Yahboom Transbot |
| SBC | Jetson Nano |
| Lidar | Intégré Transbot (SLAM + navigation) |
| Caméra | Intel RealSense (profondeur) |
| Bras robotique | Intégré Transbot (pick-up / drop-off) |
| Vitesse max | 0.3 m/s (sécurité physique) |

---

## Structure du monorepo

```
Robotique/
├── apps/
│   ├── web/                  # Front-end React + TypeScript + Tailwind
│   ├── server/               # Back-end PHP + MySQL + Socket.io
│   └── robot/                # Packages ROS 2 (Python)
│
├── packages/
│   └── shared/               # Types TypeScript partagés front ↔ back
│
├── docs/
│   ├── uml/                  # Diagrammes PlantUML (use case, séquence, états)
│   └── RAA-CDC-Complet.pdf   # Cahier des Charges complet
│
├── scripts/                  # Scripts de setup et déploiement
│
└── .github/
    └── workflows/            # CI/CD GitHub Actions (lint + tests)
```

---

## API REST

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `POST` | `/api/missions` | Créer une nouvelle mission |
| `GET` | `/api/missions` | Lister toutes les missions |
| `GET` | `/api/missions/:id` | Détail d'une mission |
| `PATCH` | `/api/missions/:id/status` | Mise à jour du statut (robot → serveur) |
| `GET` | `/api/robot/status` | État courant du robot (batterie, position) |
| `POST` | `/api/robot/emergency-stop` | Arrêt d'urgence |

---

## Events WebSocket

| Event | Direction | Description |
|-------|-----------|-------------|
| `mission:created` | Serveur → Front | Nouvelle mission créée |
| `mission:updated` | Serveur → Front | Statut mission mis à jour |
| `mission:completed` | Serveur → Front | Mission terminée |
| `mission:assign` | Serveur → Robot | Assignation de mission au robot |
| `robot:heartbeat` | Robot → Serveur | Heartbeat toutes les 5 secondes |
| `robot:position` | Robot → Front (via serveur) | Position temps réel (toutes les 500ms) |
| `robot:obstacle-detected` | Robot → Serveur | Obstacle détecté sur le trajet |

### Règles de monitoring

- **Batterie < 20%** → alerte orange dans l'interface
- **Pas de heartbeat pendant 15s** → alerte rouge "Robot déconnecté"
- **Batterie insuffisante** → mission refusée

---

## Machine à états — Mission

```
[*] ──→ CREATED ──→ ASSIGNED ──→ NAVIGATING_TO_PICKUP ──→ PICKING_UP
                                                               │
         CANCELLED ◄── CREATED                                 │
         CANCELLED ◄── ASSIGNED                                ▼
         FAILED ◄── NAVIGATING_TO_PICKUP              NAVIGATING_TO_DROP
         FAILED ◄── PICKING_UP                                 │
         FAILED ◄── NAVIGATING_TO_DROP                         ▼
         EMERGENCY_STOPPED ◄── NAVIGATING_TO_*         DROPPING_OFF
                                                               │
                                                               ▼
                                                          COMPLETED ──→ [*]
```

| Statut | Description |
|--------|-------------|
| `CREATED` | Mission créée par l'opérateur |
| `ASSIGNED` | Robot disponible, mission assignée |
| `NAVIGATING_TO_PICKUP` | Robot en route vers le point A |
| `PICKING_UP` | Bras robotique saisit l'objet |
| `NAVIGATING_TO_DROP` | Robot en route vers le point B |
| `DROPPING_OFF` | Bras robotique dépose l'objet |
| `COMPLETED` | Mission terminée avec succès |
| `CANCELLED` | Annulée par l'opérateur |
| `FAILED` | Échec (navigation, bras, timeout) |
| `EMERGENCY_STOPPED` | Arrêt d'urgence déclenché |

---

## Packages ROS 2

| Package | Fonction |
|---------|----------|
| `nav2_bringup` | Navigation autonome : planification de trajectoire + évitement d'obstacles |
| `slam_toolbox` | Cartographie initiale du lieu (SLAM) via Lidar |
| `robot_localization` | Fusion odometry + IMU pour localisation précise |
| `micro_ros_agent` | Bridge entre Jetson et microcontrôleurs du Transbot |
| `mission_manager` | Node custom : reçoit missions API, orchestre navigation + bras |
| `arm_controller` | Node custom : contrôle du bras (pick-up / drop-off) |
| `safety_monitor` | Node custom : watchdog, arrêt d'urgence, monitoring batterie |

---

## Installation

### Prérequis

- **Node.js** >= 20 LTS (pour le front-end)
- **PHP** >= 8.x + **MySQL** (pour le back-end)
- **ROS 2 Humble** (pour le robot — sur Jetson Nano)

### Front-end

```bash
cd apps/web
npm install
npm run dev
```

### Back-end

```bash
cd apps/server
# Configurer la connexion MySQL
# Lancer le serveur PHP + Socket.io
```

### Robot

```bash
cd apps/robot
colcon build
source install/setup.bash
ros2 launch raa_bringup raa.launch.py
```

---

## Branches Git

| Branche | Description |
|---------|-------------|
| `main` | Branche principale — toujours déployable, protégée |
| `Front-End` | Développement du dashboard React |
| `Back-End` | Développement du serveur PHP + API REST + WebSocket |
| `IOT` | Packages ROS 2, navigation, bras, safety monitor |

### Convention de branches features

```
feature/front-<ticket>-<slug>     # ex: feature/front-RAA-12-dashboard-missions
feature/back-<ticket>-<slug>      # ex: feature/back-RAA-21-crud-missions
feature/iot-<ticket>-<slug>       # ex: feature/iot-RAA-35-nav2-navigation
```

---

## Conventions équipe

### Commits (Conventional Commits)

```
<type>(<scope>): <description courte>
```

**Types** : `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `style`, `ci`

**Scopes** : `front`, `back`, `robot`, `api`, `db`, `ci`, `docs`

```
feat(front): add mission creation form
fix(robot): fix websocket reconnection after wifi loss
docs(api): update openapi.yaml with robot endpoints
test(back): add jest tests for mission state machine
```

### Nommage

| Contexte | Convention | Exemple |
|----------|-----------|---------|
| Variables JS/TS | camelCase | `missionStatus`, `robotPosition` |
| Composants React | PascalCase | `MissionCard`, `RobotStatusBadge` |
| Hooks custom | use + camelCase | `useMissionStatus` |
| Endpoints API | kebab-case | `/api/robot/emergency-stop` |
| Tables MySQL | snake_case | `mission_logs`, `map_points` |
| Nodes ROS 2 | snake_case | `mission_manager`, `arm_controller` |
| Topics ROS 2 | /namespace/topic | `/robot/position`, `/robot/battery` |
| Events WebSocket | namespace:action | `mission:updated`, `robot:heartbeat` |

### Pull Requests

- Toute PR doit cibler `develop` (jamais `main` directement)
- Minimum **1 reviewer** obligatoire
- La **CI doit être verte** (lint + tests) avant de merger
- Pas de self-merge
- Les merges vers `main` sont faits par le CTO uniquement

---

## Roadmap

### Sprint 0 — Fondations (Semaine 1)

| Qui | Tâches | Livrable |
|-----|--------|----------|
| Tous | Contrat API (OpenAPI 3.0) + setup Git + CI | `openapi.yaml` + repo + CI vert |
| IoT | ROS 2 sur Jetson, moteurs + Lidar + bras, SLAM cartographie | Robot fonctionnel + carte |
| Back | Setup PHP + MySQL + Socket.io | Serveur qui répond |
| Front | Setup React + Tailwind + routing + stubs API | Shell app navigable |

### Sprint 1 — Intégration verticale (Semaines 2-3)

| Qui | Tâches | Livrable |
|-----|--------|----------|
| Front | Dashboard missions + formulaire création + carte SVG + WebSocket | UI fonctionnelle + live updates |
| Back | CRUD missions + machine à états + bridge WebSocket + emergency stop | API stable + temps réel |
| IoT | Nav2 A → B + évitement obstacles + client API Python + pick/place bras | Robot navigue + connecté |

### Sprint 2 — Robustesse + Démo (Semaines 4-5)

| Qui | Tâches | Livrable |
|-----|--------|----------|
| Front | Audit WCAG AA + gestion erreurs + arrêt urgence + notifications | UX complète + accessible |
| Back | Gestion erreurs + retry + timeout missions + heartbeat + reconnexion | API robuste + résiliente |
| IoT | Tuning Nav2 + scénario démo pick → move → place + safety monitor | Démo prête |
| Tous | **10+ répétitions démo complètes** | Zéro surprise |

---

## Risques et mitigations

| Criticité | Risque | Mitigation |
|-----------|--------|------------|
| Critique | Wi-Fi instable en démo | Hotspot dédié, auto-reconnect, mode dégradé autonome |
| Critique | SLAM imprécis | Cartographier le lieu exact, balises visuelles, vitesse réduite |
| Critique | Bras ne saisit pas | Objet standardisé, séquence calibrée, plan B : plateau fixe |
| Haute | Latence WebSocket | Interpolation front, réduire fréquence, tester réseau salle |
| Haute | Batterie insuffisante | Monitoring 20%, charge complète, batterie externe |
| Haute | Sécurité physique | 0.3 m/s max, arrêt urgence, périmètre délimité, safety monitor |
| Haute | Intégration tardive | API Contract First, mock serveur + mock robot, CI dès Sprint 1 |

### Stratégie démo

- Toujours avoir un **scénario B** (simplifié) prêt
- **Filmer une vidéo** de la démo qui fonctionne la veille en backup
- Faire **10+ répétitions** complètes avant le jour J
- Apporter son propre **routeur Wi-Fi**
- Prévoir **15 min de setup** avant le passage

---

## Équipe

| Rôle | Effectif |
|------|----------|
| Front-end | 1 |
| Back-end | 2 |
| IoT / Robotique | 2 |

**HETIC Web3 — Projet RAA — Février 2026 — v1.1**
