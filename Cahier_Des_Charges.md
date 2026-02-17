# Cahier des Charges Technique — Couche IoT
## Robot Mobile Autonome de Transport Intra-Bâtiment (ERP)

---

> **Version :** 0.0.1  
> **Date :** Février 2026  
> **Statut :** Draft — En revue technique  
> **Auteur :** Équipe Ingénierie Robotique & IoT  
> **Domaine :** Couche IoT / Communication — Périmètre uniquement  
> **Stack cible :** ROS 2 Humble · ESP32-H2 · MQTT · Node.js · React  

---

## Table des matières

1. [Introduction et objectifs](#1-introduction-et-objectifs)
2. [Périmètre fonctionnel IoT](#2-périmètre-fonctionnel-iot)
3. [Architecture système détaillée](#3-architecture-système-détaillée)
4. [Description des composants](#4-description-des-composants)
5. [Flux de données](#5-flux-de-données)
6. [Topics MQTT normalisés](#6-topics-mqtt-normalisés)
7. [Cas d'usage détaillés](#7-cas-dusage-détaillés)
8. [Gestion des erreurs et alertes](#8-gestion-des-erreurs-et-alertes)
9. [Contraintes techniques](#9-contraintes-techniques)
10. [Sécurité et fiabilité](#10-sécurité-et-fiabilité)
11. [Scalabilité multi-robots](#11-scalabilité-multi-robots)
12. [Diagrammes d'architecture](#12-diagrammes-darchitecture)
13. [Critères d'acceptation](#13-critères-dacceptation)
14. [Évolutions futures possibles](#14-évolutions-futures-possibles)
15. [Glossaire](#15-glossaire)

---

## 1. Introduction et objectifs

### 1.1 Contexte

Ce document constitue le **cahier des charges technique de la couche IoT** d'un robot mobile autonome destiné au transport d'objets dans un environnement ERP (Établissement Recevant du Public) multi-étages. Le robot utilise **ROS 2 Humble** comme couche de navigation et d'intelligence embarquée.

Le système IoT a pour rôle de jouer le rôle de **pont de communication** entre le robot (monde ROS 2, temps réel) et le reste de l'infrastructure numérique : backend applicatif, interfaces utilisateur, systèmes de supervision et services d'alerte.

Ce document ne couvre **pas** les aspects suivants (hors périmètre) :
- Architecture de navigation ROS 2 (Navigation2, AMCL, SLAM)
- Mécanique du robot, motorisation, capteurs de navigation
- Infrastructure réseau physique du bâtiment
- Application métier de gestion des missions

### 1.2 Objectifs du système IoT

| Priorité | Objectif | Description |
|----------|----------|-------------|
| P0 | Supervision temps réel | Remonter en continu l'état du robot vers le dashboard |
| P0 | Détection d'anomalies embarquée | L'ESP32-H2 détecte localement les situations anormales |
| P0 | Commandabilité distante | Permettre l'envoi de commandes (arrêt, reprise, mission) |
| P1 | Journalisation d'événements | Conserver un historique exploitable des états et alertes |
| P2 | Scalabilité multi-robots | Permettre la supervision de N robots simultanément |
| P2 | Sécurité des communications | Authentification, chiffrement, contrôle d'accès |

### 1.3 Références normatives et techniques

| Référence | Description |
|-----------|-------------|
| ROS 2 REP-2000 | Politique de support des distributions ROS 2 |
| MQTT v5.0 (OASIS) | Spécification du protocole MQTT |
| RFC 8259 | Format JSON (IETF) |
| ESP-IDF v5.x | Framework officiel Espressif pour ESP32 |
| IEC 62443 | Sécurité des systèmes de contrôle industriels (référence) |
| ISO 13849 | Sécurité fonctionnelle des machines (référence) |

---

## 2. Périmètre fonctionnel IoT

### 2.1 Fonctions incluses dans le périmètre IoT

```
┌────────────────────────────────────────────────────────┐
│                   PÉRIMÈTRE IoT                        │
│                                                        │
│  ✅ Collecte des données de télémétrie ROS 2           │
│  ✅ Transmission UART ROS 2 ↔ ESP32-H2                 │
│  ✅ Publication MQTT vers le broker                    │
│  ✅ Réception et dispatch de commandes distantes       │
│  ✅ Détection locale d'anomalies (watchdog embarqué)   │
│  ✅ Gestion de l'état multi-étages                     │
│  ✅ API REST / WebSocket backend Node.js               │
│  ✅ Dashboard React temps réel                         │
│  ✅ Système d'alertes et notifications                 │
│  ✅ Journalisation et persistance des événements       │
└────────────────────────────────────────────────────────┘
```

### 2.2 Frontières du système IoT

```
┌─────────────────┐    FRONTIÈRE     ┌─────────────────────┐
│   ROS 2 (SBC)   │ ◄── UART / ──► │   ESP32-H2 (IoT GW) │
│  Navigation,    │   Serial JSON    │   Passerelle IoT    │
│  Planification  │                  │   MQTT Publisher    │
└─────────────────┘                  └─────────────────────┘
         ↑                                      ↑
    Hors périmètre                       Dans périmètre
    (doc navigation)                      (ce document)
```

### 2.3 Données télémétrique collectées

| Catégorie | Données | Fréquence cible | Source ROS 2 |
|-----------|---------|-----------------|--------------|
| Localisation | Position (x, y), orientation (yaw) | 2 Hz | `/amcl_pose` |
| Cinématique | Vitesse linéaire, vitesse angulaire | 5 Hz | `/cmd_vel`, `/odom` |
| Mission | État mission, point courant, destination | Événementiel | Mission Manager |
| Batterie | Niveau (%), tension (V), état charge | 0.2 Hz | `/battery_state` |
| Navigation | État Nav2, coût trajectoire, mode | 1 Hz | `/navigate_to_pose` |
| Étage | Étage courant, carte ROS 2 active | Événementiel | Map Manager |
| Système | CPU, RAM, température SBC | 0.1 Hz | Nœud diagnostic |
| Alertes | Blocage, collision évitée, erreur | Événementiel | Nodes ROS 2 |

### 2.4 Commandes distantes supportées

| Commande | Description | Paramètres |
|----------|-------------|------------|
| `STOP_EMERGENCY` | Arrêt d'urgence immédiat | — |
| `PAUSE_MISSION` | Mise en pause de la mission en cours | — |
| `RESUME_MISSION` | Reprise de la mission en pause | — |
| `CANCEL_MISSION` | Annulation et retour à la base | — |
| `SEND_TO_WAYPOINT` | Envoi vers un point de passage | `{waypoint_id}` |
| `SEND_TO_COORDINATES` | Envoi vers des coordonnées absolues | `{x, y, floor}` |
| `REQUEST_STATUS` | Demande de rapport d'état complet | — |
| `RESET_WATCHDOG` | Réinitialisation du watchdog ESP32 | — |

---

## 3. Architecture système détaillée

### 3.1 Vue d'ensemble

L'architecture IoT repose sur un modèle **publish/subscribe** avec le protocole MQTT comme épine dorsale de communication. Le flux de données suit une chaîne unidirectionnelle (robot → cloud) pour la télémétrie, et bidirectionnelle pour les commandes.

```
                    ╔══════════════════════════════════════════╗
                    ║           ROBOT EMBARQUÉ                 ║
                    ║                                          ║
  ┌─────────────┐   ║  ┌──────────────────────────────────┐   ║
  │  Capteurs   │──►║  │         ROS 2 Humble             │   ║
  │  LiDAR      │   ║  │  - Navigation2 (Nav2)            │   ║
  │  Caméra     │   ║  │  - AMCL (localisation)           │   ║
  │  Encodeurs  │   ║  │  - SLAM (cartographie)           │   ║
  │  IMU        │   ║  │  - Mission Manager               │   ║
  └─────────────┘   ║  │  - IoT Bridge Node               │   ║
                    ║  └──────────────┬───────────────────┘   ║
                    ║                 │ UART (Serial JSON)     ║
                    ║  ┌──────────────▼───────────────────┐   ║
                    ║  │         ESP32-H2                  │   ║
                    ║  │  (Passerelle IoT - Gateway)       │   ║
                    ║  │  - Parser UART / Sérialiseur      │   ║
                    ║  │  - MQTT Client (TLS)              │   ║
                    ║  │  - Watchdog Robot                 │   ║
                    ║  │  - Détection d'anomalies          │   ║
                    ║  │  - Buffer local (NVS)             │   ║
                    ║  └──────────────┬───────────────────┘   ║
                    ╚═════════════════╪════════════════════════╝
                                      │ MQTT over TLS (WiFi)
                    ╔═════════════════▼════════════════════════╗
                    ║        INFRASTRUCTURE CLOUD / LAN         ║
                    ║                                          ║
                    ║  ┌──────────────────────────────────┐   ║
                    ║  │       MQTT Broker (Mosquitto)     │   ║
                    ║  │       ou HiveMQ / EMQX            │   ║
                    ║  └──────────┬───────────────┬────────┘   ║
                    ║             │               │             ║
                    ║  ┌──────────▼──────┐  ┌────▼───────┐   ║
                    ║  │  Node.js        │  │  Subscriber │   ║
                    ║  │  Backend API    │  │  Alerting   │   ║
                    ║  │  - REST API     │  │  Service    │   ║
                    ║  │  - WebSocket    │  └────────────┘   ║
                    ║  │  - MQTT Client  │                     ║
                    ║  │  - TimescaleDB  │                     ║
                    ║  └──────────┬──────┘                     ║
                    ║             │ WebSocket                   ║
                    ║  ┌──────────▼──────┐                     ║
                    ║  │  React Dashboard│                     ║
                    ║  │  - Carte temps  │                     ║
                    ║  │    réel         │                     ║
                    ║  │  - Alertes      │                     ║
                    ║  │  - Historique   │                     ║
                    ║  └─────────────────┘                     ║
                    ╚══════════════════════════════════════════╝
```

### 3.2 Couches de l'architecture

| Couche | Technologie | Rôle |
|--------|-------------|------|
| **L1 - Capteurs** | LiDAR, IMU, encodeurs | Perception du monde physique |
| **L2 - ROS 2** | Navigation2, AMCL | Intelligence de navigation |
| **L3 - IoT Bridge** | Nœud ROS 2 dédié | Agrégation et serialisation des topics |
| **L4 - Gateway** | ESP32-H2 | Passerelle protocole, watchdog, MQTT |
| **L5 - Transport** | MQTT v5 over TLS 1.3 | Transport sécurisé des données |
| **L6 - Broker** | Mosquitto / EMQX | Distribution des messages |
| **L7 - Backend** | Node.js + TypeScript | API, persistance, agrégation |
| **L8 - Frontend** | React + WebSocket | Supervision temps réel |

---

## 4. Description des composants

### 4.1 Nœud ROS 2 — IoT Bridge Node

#### 4.1.1 Responsabilités

Le nœud `iot_bridge_node` est un nœud ROS 2 développé en Python (ou C++) qui agit comme **agrégateur** de l'ensemble des topics pertinents à exposer vers la couche IoT. Il est le **seul point de contact** entre ROS 2 et l'ESP32-H2.

#### 4.1.2 Subscriptions ROS 2

| Topic ROS 2 | Type de message | Fréquence |
|-------------|-----------------|-----------|
| `/amcl_pose` | `geometry_msgs/PoseWithCovarianceStamped` | 2 Hz |
| `/odom` | `nav_msgs/Odometry` | 5 Hz |
| `/cmd_vel` | `geometry_msgs/Twist` | 5 Hz |
| `/battery_state` | `sensor_msgs/BatteryState` | 0.2 Hz |
| `/navigate_to_pose/_action/status` | `action_msgs/GoalStatusArray` | 1 Hz |
| `/diagnostics` | `diagnostic_msgs/DiagnosticArray` | 1 Hz |
| `/map_metadata` | `nav_msgs/MapMetaData` | Événementiel |
| `/current_floor` | `std_msgs/String` (custom) | Événementiel |
| `/mission_status` | Custom message | Événementiel |

#### 4.1.3 Format de sortie UART

Le nœud publie sur le port UART un **JSON compact** (terminé par `\n`) à intervalles réguliers ou lors d'événements :

```json
{
  "ts": 1708945200123,
  "robot_id": "robot_01",
  "type": "telemetry",
  "payload": {
    "pose": { "x": 12.45, "y": 8.32, "yaw": 1.57 },
    "velocity": { "linear": 0.35, "angular": 0.02 },
    "battery": { "percent": 78, "voltage": 24.1 },
    "nav_state": "ACTIVE",
    "mission": {
      "id": "mission_042",
      "status": "IN_PROGRESS",
      "origin": "A2",
      "destination": "B7"
    },
    "floor": { "id": "floor_2", "map_name": "batiment_etage2" }
  }
}
```

#### 4.1.4 Réception de commandes UART

Le nœud écoute également les trames UART entrantes et les traduit en actions ROS 2 (publication sur topics de commande, appel d'action servers).

```json
{
  "ts": 1708945200000,
  "cmd": "SEND_TO_WAYPOINT",
  "params": { "waypoint_id": "B7" },
  "request_id": "req_abc123"
}
```

### 4.2 ESP32-H2 — Passerelle IoT

#### 4.2.1 Caractéristiques matérielles

| Paramètre | Valeur |
|-----------|--------|
| MCU | ESP32-H2 (RISC-V 32-bit, 96 MHz) |
| RAM | 320 KB SRAM |
| Flash | 4 MB (minimum) |
| Connectivité | WiFi 802.11 b/g/n (via module externe) / Thread / Zigbee |
| UART | 2× UART hardware disponibles |
| Framework | ESP-IDF v5.x |
| Alimentation | 3.3V — alimenté par SBC robot |

> **Note :** L'ESP32-H2 est un SoC orienté Thread/Zigbee/BLE. Pour les déploiements nécessitant une connectivité WiFi native robuste, envisager un **ESP32-S3** ou un module ESP32-H2 couplé à un module WiFi externe. Ce document suppose une connectivité WiFi disponible via coprocesseur ou module.

#### 4.2.2 Architecture logicielle ESP32-H2 (FreeRTOS)

```
┌──────────────────────────────────────────────────────────┐
│                    ESP-IDF Application                    │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  UART Task   │  │  MQTT Task   │  │ Watchdog Task │  │
│  │  (Priority 5)│  │  (Priority 4)│  │ (Priority 6)  │  │
│  └──────┬───────┘  └──────┬───────┘  └───────┬───────┘  │
│         │                 │                   │           │
│  ┌──────▼─────────────────▼───────────────────▼───────┐  │
│  │              Message Queue (FreeRTOS)               │  │
│  │     uart_rx_queue | mqtt_tx_queue | alert_queue     │  │
│  └──────────────────────────────────────────────────┬─┘  │
│                                                      │     │
│  ┌───────────────────────────────────────────────────▼─┐  │
│  │              Core Processing Layer                   │  │
│  │  - JSON Parser (cJSON)                              │  │
│  │  - Anomaly Detector                                 │  │
│  │  - State Machine (robot state)                      │  │
│  │  - NVS Buffer (stockage local NVS)                  │  │
│  └─────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

#### 4.2.3 Watchdog Robot (détection de blocage)

La détection de blocage est implémentée dans une tâche dédiée haute priorité.

**Algorithme de détection :**

```
VARIABLES:
  v_cmd       : vitesse commandée (reçue de ROS 2)
  v_real      : vitesse odométrique réelle
  T_THRESHOLD : 5 secondes (configurable)
  V_CMD_MIN   : 0.05 m/s (seuil de commande "active")
  V_REAL_MAX  : 0.02 m/s (seuil de "quasi-immobilité")

ALGORITHME:
  timer_stuck ← 0

  BOUCLE INFINIE (toutes les 100ms):
    SI (|v_cmd| > V_CMD_MIN) ET (|v_real| < V_REAL_MAX):
      timer_stuck ← timer_stuck + 100ms
      SI timer_stuck >= T_THRESHOLD:
        ÉMETTRE alerte MQTT "ROBOT_STUCK"
        JOURNALISER événement en NVS
        timer_stuck ← 0  // éviter répétition immédiate
    SINON:
      timer_stuck ← 0
    FIN SI
  FIN BOUCLE
```

**Topic MQTT émis :**
```json
{
  "ts": 1708945200000,
  "robot_id": "robot_01",
  "alert_type": "ROBOT_STUCK",
  "severity": "HIGH",
  "details": {
    "v_commanded_ms": 0.35,
    "v_real_ms": 0.01,
    "duration_stuck_s": 5.1,
    "position": { "x": 12.45, "y": 8.32, "floor": "floor_2" }
  }
}
```

#### 4.2.4 Gestion du buffer local (NVS)

En cas de perte de connectivité WiFi/MQTT, l'ESP32-H2 stocke les messages critiques dans sa mémoire NVS (Non-Volatile Storage) avec une stratégie FIFO et taille maximale configurable (ex. : 100 messages). À la reconnexion, les messages sont renvoyés dans l'ordre chronologique.

| Paramètre NVS | Valeur par défaut |
|---------------|-------------------|
| Taille max buffer | 100 messages |
| Politique overflow | Drop oldest |
| Namespace NVS | `robot_iot` |
| Clé index | `buf_head`, `buf_tail`, `buf_count` |

### 4.3 MQTT Broker

| Paramètre | Valeur recommandée |
|-----------|-------------------|
| Logiciel | Mosquitto 2.x (on-premise) ou EMQX (cloud) |
| Port TLS | 8883 |
| Port WS/WSS | 8083 / 8084 |
| Authentification | Username/password + certificat client TLS |
| QoS par défaut | QoS 1 (at least once) |
| Rétention | Activée sur topics d'état (`/status`) |
| Persistent session | Activée pour le backend subscriber |
| Will Message | Configuré sur topic `/robot/{id}/connection` |

### 4.4 Backend Node.js

#### 4.4.1 Responsabilités

- Subscriber MQTT → agrégation et normalisation des données
- Persistance en base de données temporelle (TimescaleDB / InfluxDB)
- API REST pour les requêtes historiques et la configuration
- Serveur WebSocket pour le push temps réel vers le dashboard
- Moteur de règles d'alerte configurables
- Gestionnaire d'authentification et d'autorisation

#### 4.4.2 Stack technique recommandée

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Runtime | Node.js | ≥ 20 LTS |
| Langage | TypeScript | ≥ 5.x |
| MQTT Client | `mqtt.js` | ≥ 5.x |
| WebSocket | `socket.io` | ≥ 4.x |
| API REST | Fastify | ≥ 4.x |
| Base de données | TimescaleDB (PostgreSQL) | ≥ 2.x |
| ORM / Query Builder | Drizzle ORM | ≥ 0.30 |
| Validation schéma | Zod | ≥ 3.x |
| Authentification | JWT + Refresh Token | — |

#### 4.4.3 Endpoints REST principaux

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/robots` | Liste tous les robots enregistrés |
| `GET` | `/api/robots/{id}/status` | État courant d'un robot |
| `GET` | `/api/robots/{id}/telemetry?from=&to=` | Historique de télémétrie |
| `GET` | `/api/robots/{id}/alerts?limit=` | Historique des alertes |
| `POST` | `/api/robots/{id}/command` | Envoi d'une commande au robot |
| `GET` | `/api/buildings/{id}/floors` | Configuration des étages |
| `GET` | `/api/missions` | Liste des missions actives et passées |
| `POST` | `/api/missions` | Création d'une nouvelle mission |

### 4.5 Dashboard React

#### 4.5.1 Composants principaux

| Composant | Description | Données temps réel |
|-----------|-------------|-------------------|
| `RobotMapView` | Carte du bâtiment avec position robot | Position, orientation |
| `StatusPanel` | État général du robot | Tous les champs télémétrie |
| `BatteryWidget` | Indicateur de batterie | Niveau, état charge |
| `MissionTimeline` | Progression de la mission | Étapes, ETA, statut |
| `AlertFeed` | Flux des alertes en temps réel | Alertes push |
| `FloorSelector` | Changement d'affichage par étage | Carte active |
| `CommandPanel` | Panneau de commandes manuelles | — |
| `TelemetryChart` | Graphiques vitesse/batterie | Historique 1h |

#### 4.5.2 Connexion WebSocket

```javascript
// Exemple d'intégration Socket.io côté client React
const socket = io('wss://backend.example.com', {
  auth: { token: userJWT },
  transports: ['websocket']
});

// Souscription aux mises à jour d'un robot spécifique
socket.emit('subscribe', { robot_id: 'robot_01' });

socket.on('telemetry_update', (data) => {
  // Mise à jour de l'état React
  dispatch(updateRobotState(data));
});

socket.on('alert', (alert) => {
  // Affichage notification + toast
  dispatch(pushAlert(alert));
});

socket.on('floor_change', (event) => {
  // Rechargement de la carte correspondante
  dispatch(changeFloorMap(event.floor_id));
});
```

---

## 5. Flux de données

### 5.1 Flux de télémétrie (Robot → Dashboard)

```
ROS 2 Node           ESP32-H2              MQTT Broker       Node.js          React
    │                    │                      │               │                │
    │ Publish topics     │                      │               │                │
    │ /amcl_pose         │                      │               │                │
    │ /odom              │                      │               │                │
    │ /battery_state     │                      │               │                │
    │                    │                      │               │                │
    │──── JSON\n ───────►│                      │               │                │
    │     (UART)         │                      │               │                │
    │                    │ Parse + Validate      │               │                │
    │                    │ Watchdog check        │               │                │
    │                    │──── PUBLISH ─────────►│               │                │
    │                    │ robot/01/telemetry    │               │                │
    │                    │ QoS 1, TLS            │               │                │
    │                    │                      │──── DELIVER ──►│                │
    │                    │                      │               │                │
    │                    │                      │               │ Persist to DB   │
    │                    │                      │               │ Normalize data  │
    │                    │                      │               │──── WS event ──►│
    │                    │                      │               │  telemetry_upd  │
    │                    │                      │               │                │ Update UI
```

### 5.2 Flux de commande (Dashboard → Robot)

```
React               Node.js            MQTT Broker       ESP32-H2          ROS 2 Node
  │                    │                    │                │                  │
  │ POST /api/robots/  │                    │                │                  │
  │ 01/command         │                    │                │                  │
  │ {cmd: PAUSE}       │                    │                │                  │
  │───────────────────►│                    │                │                  │
  │                    │ Validate + Auth     │                │                  │
  │                    │ Log command         │                │                  │
  │                    │──── PUBLISH ───────►│                │                  │
  │                    │ robot/01/cmd        │                │                  │
  │                    │ QoS 2               │                │                  │
  │  HTTP 202          │                    │──── DELIVER ──►│                  │
  │◄───────────────────│                    │                │                  │
  │  {request_id: ..}  │                    │                │ Parse command     │
  │                    │                    │                │──── UART TX ─────►│
  │                    │                    │                │  JSON command     │
  │                    │                    │                │                  │ Execute ROS 2
  │                    │                    │                │                  │ action/service
  │                    │                    │                │◄── ACK UART ──────│
  │                    │                    │◄── PUBLISH ────│                  │
  │                    │                    │ robot/01/ack    │                  │
  │                    │◄── DELIVER ────────│                │                  │
  │◄── WS event ───────│                    │                │                  │
  │  command_ack        │                    │                │                  │
```

### 5.3 Flux de changement d'étage

```
ROS 2 Map Manager    IoT Bridge           ESP32-H2          MQTT Broker      Dashboard
       │                  │                   │                  │                │
       │ /current_floor   │                   │                  │                │
       │ "floor_2"        │                   │                  │                │
       │─────────────────►│                   │                  │                │
       │                  │ Build floor_change│                  │                │
       │                  │ JSON message      │                  │                │
       │                  │──── UART TX ─────►│                  │                │
       │                  │                   │ Publish          │                │
       │                  │                   │─────────────────►│                │
       │                  │                   │ robot/01/floor   │                │
       │                  │                   │ (retained msg)   │                │
       │                  │                   │                  │──── DELIVER ──►│
       │                  │                   │                  │                │ Load new
       │                  │                   │                  │                │ floor map
       │                  │                   │                  │                │ Re-center view
       │                  │                   │                  │                │ Show transition
```

### 5.4 Flux de détection d'anomalie (watchdog embarqué)

```
ESP32-H2 Watchdog Task                  MQTT Broker         Node.js          Alerting
         │                                   │                  │                │
         │ v_cmd > 0.05 m/s                  │                  │                │
         │ v_real < 0.02 m/s                 │                  │                │
         │ depuis 5.0 secondes               │                  │                │
         │                                   │                  │                │
         │ ──── PUBLISH ALERT ──────────────►│                  │                │
         │ robot/01/alerts/stuck             │                  │                │
         │ QoS 1, severity: HIGH             │                  │                │
         │                                   │──── DELIVER ─────►│                │
         │                                   │                  │ Persist alert  │
         │                                   │                  │ Trigger rules  │
         │                                   │                  │────────────────►│
         │                                   │                  │ Email/SMS/Push │
         │                                   │◄── PUBLISH ───────│                │
         │                                   │ robot/01/cmd      │                │
         │ ◄── DELIVER ──────────────────────│                  │                │
         │ Receive: REQUEST_STATUS           │                  │                │
```

---

## 6. Topics MQTT normalisés

### 6.1 Convention de nommage

```
robot/{robot_id}/{category}/{subcategory}
```

- `{robot_id}` : identifiant unique du robot (ex. : `robot_01`, `robot_lab_02`)
- `{category}` : domaine fonctionnel
- `{subcategory}` : précision optionnelle

### 6.2 Table complète des topics

#### Topics de télémétrie (ESP32 → Broker)

| Topic | QoS | Retain | Fréquence | Description |
|-------|-----|--------|-----------|-------------|
| `robot/{id}/telemetry` | 1 | Non | 2 Hz | Agrégat principal (position, vitesse, état) |
| `robot/{id}/telemetry/pose` | 1 | Oui | 2 Hz | Position et orientation uniquement |
| `robot/{id}/telemetry/velocity` | 1 | Non | 5 Hz | Vitesse linéaire et angulaire |
| `robot/{id}/telemetry/battery` | 1 | Oui | 0.2 Hz | État batterie complet |
| `robot/{id}/status` | 1 | Oui | Événementiel | État global du robot (retained) |
| `robot/{id}/mission` | 1 | Oui | Événementiel | État mission courante (retained) |
| `robot/{id}/floor` | 1 | Oui | Événementiel | Étage et carte ROS 2 active (retained) |
| `robot/{id}/diagnostics` | 0 | Non | 0.1 Hz | Métriques système (CPU, RAM, temp) |
| `robot/{id}/connection` | 1 | Oui | Connexion/déco | Will message de présence |

#### Topics d'alertes (ESP32 → Broker)

| Topic | QoS | Retain | Description |
|-------|-----|--------|-------------|
| `robot/{id}/alerts` | 1 | Non | Canal général des alertes |
| `robot/{id}/alerts/stuck` | 1 | Non | Robot détecté bloqué |
| `robot/{id}/alerts/battery_low` | 1 | Non | Batterie sous seuil critique |
| `robot/{id}/alerts/navigation_error` | 1 | Non | Échec de navigation Nav2 |
| `robot/{id}/alerts/floor_transition` | 1 | Non | Début/fin de transition ascenseur |
| `robot/{id}/alerts/uart_timeout` | 1 | Non | Perte de communication UART |
| `robot/{id}/alerts/connectivity_lost` | 1 | Non | Perte WiFi (depuis Will Message) |

#### Topics de commande (Broker → ESP32)

| Topic | QoS | Description |
|-------|-----|-------------|
| `robot/{id}/cmd` | 2 | Commandes générales (STOP, PAUSE, RESUME) |
| `robot/{id}/cmd/mission` | 2 | Commandes de mission (SEND_TO, CANCEL) |
| `robot/{id}/cmd/config` | 1 | Mise à jour de configuration distante |

#### Topics d'acquittement (ESP32 → Broker)

| Topic | QoS | Description |
|-------|-----|-------------|
| `robot/{id}/ack/{request_id}` | 1 | Accusé de réception d'une commande |

#### Topics de supervision globale (multi-robots)

| Topic | QoS | Retain | Description |
|-------|-----|--------|-------------|
| `fleet/status` | 1 | Oui | État agrégé de la flotte |
| `fleet/alerts` | 1 | Non | Alertes de niveau flotte |
| `building/{id}/floor/{floor}/occupancy` | 1 | Oui | Robots présents par étage |

### 6.3 Schéma JSON des messages principaux

#### Message `robot/{id}/telemetry`

```json
{
  "$schema": "https://robot-iot.example.com/schemas/telemetry/v1",
  "ts": 1708945200123,
  "robot_id": "robot_01",
  "schema_version": "1.0",
  "pose": {
    "x": 12.45,
    "y": 8.32,
    "yaw": 1.5707,
    "covariance_xy": 0.012
  },
  "velocity": {
    "linear_ms": 0.350,
    "angular_rads": 0.020
  },
  "battery": {
    "percent": 78,
    "voltage_v": 24.1,
    "current_a": -2.3,
    "status": "DISCHARGING"
  },
  "navigation": {
    "state": "ACTIVE",
    "planner": "NavfnPlanner",
    "goal_distance_m": 5.2
  },
  "mission": {
    "id": "mission_042",
    "status": "IN_PROGRESS",
    "origin_id": "A2",
    "destination_id": "B7",
    "eta_s": 45
  },
  "floor": {
    "id": "floor_2",
    "map_name": "batiment_etage2",
    "transition_state": "STABLE"
  },
  "system": {
    "cpu_percent": 42,
    "ram_percent": 61,
    "temp_celsius": 58
  }
}
```

#### Message `robot/{id}/alerts/stuck`

```json
{
  "ts": 1708945300456,
  "robot_id": "robot_01",
  "alert_id": "alert_20240226_001",
  "alert_type": "ROBOT_STUCK",
  "severity": "HIGH",
  "source": "ESP32_WATCHDOG",
  "details": {
    "v_commanded_ms": 0.350,
    "v_real_ms": 0.008,
    "stuck_duration_s": 5.1,
    "position": {
      "x": 12.45,
      "y": 8.32,
      "floor": "floor_2"
    },
    "mission_id": "mission_042"
  },
  "auto_actions_taken": ["STATUS_REQUESTED"]
}
```

#### Message `robot/{id}/cmd`

```json
{
  "ts": 1708945400000,
  "request_id": "req_abc123def456",
  "cmd": "SEND_TO_WAYPOINT",
  "params": {
    "waypoint_id": "B7",
    "floor": "floor_2",
    "priority": "NORMAL"
  },
  "issued_by": "user_admin_01",
  "timeout_s": 30
}
```

#### Message `robot/{id}/floor` (changement d'étage)

```json
{
  "ts": 1708945500789,
  "robot_id": "robot_01",
  "event": "FLOOR_CHANGE",
  "previous_floor": {
    "id": "floor_1",
    "map_name": "batiment_etage1"
  },
  "current_floor": {
    "id": "floor_2",
    "map_name": "batiment_etage2"
  },
  "transition_via": "ELEVATOR_A",
  "transition_state": "COMPLETE",
  "relocation_confidence": 0.94
}
```

#### Will Message `robot/{id}/connection`

```json
{
  "ts": 1708945600000,
  "robot_id": "robot_01",
  "status": "OFFLINE",
  "reason": "UNEXPECTED_DISCONNECT"
}
```

---

## 7. Cas d'usage détaillés

### UC-01 : Démarrage du robot et connexion IoT

**Acteurs :** Robot, ESP32-H2, Broker MQTT, Backend  
**Préconditions :** Robot allumé, WiFi disponible

| Étape | Acteur | Action |
|-------|--------|--------|
| 1 | ESP32-H2 | Démarrage FreeRTOS, initialisation NVS, chargement config |
| 2 | ESP32-H2 | Connexion WiFi (retries exponentiels) |
| 3 | ESP32-H2 | Connexion TLS au broker MQTT avec certificat client |
| 4 | ESP32-H2 | Publication du Will Message configuré sur `/connection` |
| 5 | ESP32-H2 | Souscription aux topics `/cmd` et `/cmd/mission` |
| 6 | ESP32-H2 | Publication `{"status": "ONLINE"}` sur `/connection` (retained) |
| 7 | ROS 2 | Démarrage des nœuds, lancement de `iot_bridge_node` |
| 8 | ROS 2 | Début de la publication UART vers ESP32-H2 |
| 9 | ESP32-H2 | Premier message télémétrie publié sur MQTT |
| 10 | Backend | Détection de la mise en ligne, mise à jour de l'état robot en DB |

**Postconditions :** Robot visible et supervisé sur le dashboard

### UC-02 : Mission de transport A → B

**Acteurs :** Opérateur, Dashboard, Backend, Robot  
**Préconditions :** Robot en ligne, mission créée dans le système

| Étape | Acteur | Action |
|-------|--------|--------|
| 1 | Opérateur | Crée une mission via dashboard (origine A2, destination B7) |
| 2 | Backend | Valide la mission, persiste en DB, publie commande MQTT |
| 3 | ESP32-H2 | Reçoit commande `SEND_TO_WAYPOINT`, transmet via UART |
| 4 | ROS 2 | `iot_bridge_node` reçoit commande, lance action Nav2 |
| 5 | ROS 2 | Navigation autonome vers B7 (planification globale + locale) |
| 6 | ESP32-H2 | Publication continue de télémétrie pendant la navigation |
| 7 | Dashboard | Affichage temps réel de la position, ETA, vitesse |
| 8 | ROS 2 | Arrivée à destination, publication `mission_status: COMPLETED` |
| 9 | ESP32-H2 | Publication événement mission terminée sur MQTT |
| 10 | Backend | Mise à jour de la mission en DB, notification opérateur |

### UC-03 : Détection de robot bloqué

**Acteurs :** ESP32-H2 Watchdog, Backend, Opérateur  
**Préconditions :** Robot en mission, navigation active

| Étape | Acteur | Action |
|-------|--------|--------|
| 1 | ESP32-H2 | Détecte : v_cmd > 0.05 m/s et v_real < 0.02 m/s depuis 5s |
| 2 | ESP32-H2 | Publie alerte `ROBOT_STUCK` sur `robot/01/alerts/stuck` (QoS 1) |
| 3 | ESP32-H2 | Journalise l'événement en NVS |
| 4 | Backend | Reçoit l'alerte, persist, déclenche moteur de règles |
| 5 | Backend | Publie commande `REQUEST_STATUS` sur `robot/01/cmd` |
| 6 | Dashboard | Affiche alerte temps réel, badge rouge sur robot |
| 7 | Backend | Envoie notification (email/push/SMS) selon config |
| 8 | Opérateur | Voit l'alerte, évalue la situation via le live feed |
| 9 | Opérateur | Décide : PAUSE_MISSION ou CANCEL_MISSION |
| 10 | ESP32-H2 | Reçoit commande, transmet à ROS 2 via UART |

### UC-04 : Transition inter-étages (ascenseur)

**Acteurs :** ROS 2, ESP32-H2, Backend, Dashboard  
**Préconditions :** Robot arrivé devant l'ascenseur, mission multi-étages

| Étape | Acteur | Action |
|-------|--------|--------|
| 1 | ROS 2 | Détecte approche point d'ascenseur, publie `/current_floor` changement |
| 2 | ROS 2 | Émet événement `FLOOR_TRANSITION_START` vers IoT Bridge |
| 3 | ESP32-H2 | Publie alerte `floor_transition` `{"state": "ENTERING_ELEVATOR"}` |
| 4 | ESP32-H2 | Active mode supervision renforcé (fréquence x2) |
| 5 | ROS 2 | Contrôle ascenseur (via interface dédiée hors périmètre) |
| 6 | ROS 2 | Déchargement carte étage 1, chargement carte étage 2 |
| 7 | ROS 2 | Relocalisation AMCL sur nouvelle carte (SLAM initial si nécessaire) |
| 8 | ROS 2 | Publie nouvelle carte active + score de confiance localisation |
| 9 | ESP32-H2 | Publie `robot/01/floor` avec `transition_state: COMPLETE` (retained) |
| 10 | Dashboard | Bascule automatiquement sur la carte du nouvel étage |
| 11 | ESP32-H2 | Retour fréquence de supervision normale |

**Gestion de la perte de signal WiFi en ascenseur :**
- L'ESP32-H2 bufferise les messages en NVS
- À la reconnexion, flush ordonné des messages bufferisés
- Le backend reconstruit la continuité temporelle depuis les timestamps

### UC-05 : Perte de connectivité et reprise

**Acteurs :** ESP32-H2, Broker MQTT, Backend  
**Préconditions :** Robot en mission

| Étape | Acteur | Action |
|-------|--------|--------|
| 1 | Réseau | Perte de connectivité WiFi |
| 2 | ESP32-H2 | Détecte perte (MQTT disconnect callback) |
| 3 | ESP32-H2 | Active buffer NVS, commence stockage local |
| 4 | ESP32-H2 | Tente reconnexion WiFi (backoff exponentiel : 1s, 2s, 4s, 8s...) |
| 5 | Broker | Will Message livré → backend marque robot `CONNECTIVITY_DEGRADED` |
| 6 | Dashboard | Affiche indicateur de perte de signal, dernière position connue |
| 7 | ESP32-H2 | Reconnexion WiFi réussie → reconnexion MQTT avec session persistante |
| 8 | ESP32-H2 | Flush NVS buffer : envoi des messages dans l'ordre chronologique |
| 9 | Backend | Intègre les données manquantes, reconstruit la timeline |
| 10 | Dashboard | Retour à l'état normal, signal vert |

---

## 8. Gestion des erreurs et alertes

### 8.1 Classification des alertes

| Niveau | Code | Couleur | Description | Délai de traitement |
|--------|------|---------|-------------|---------------------|
| CRITICAL | 0 | Rouge vif | Arrêt d'urgence, sécurité physique | Immédiat (< 1s) |
| HIGH | 1 | Rouge | Blocage, panne, navigation impossible | < 30s |
| MEDIUM | 2 | Orange | Batterie faible, ralentissement | < 5 min |
| LOW | 3 | Jaune | Anomalie mineure, dégradation partielle | < 1h |
| INFO | 4 | Bleu | Événement informatif (changement d'étage, fin mission) | — |

### 8.2 Catalogue des alertes

| Code Alerte | Sévérité | Source | Condition | Action automatique |
|-------------|----------|--------|-----------|-------------------|
| `ROBOT_STUCK` | HIGH | ESP32 Watchdog | v_cmd > 0 et v_real ≈ 0 pendant T_THRESH | REQUEST_STATUS |
| `BATTERY_CRITICAL` | HIGH | IoT Bridge | Batterie < 10% | CANCEL_MISSION + RETURN_HOME |
| `BATTERY_LOW` | MEDIUM | IoT Bridge | Batterie < 20% | Notification opérateur |
| `NAV2_ABORTED` | HIGH | IoT Bridge | Status Nav2 = ABORTED | Notification + REQUEST_STATUS |
| `UART_TIMEOUT` | CRITICAL | ESP32 | Pas de trame UART depuis 10s | Alerte, attente recovery |
| `MQTT_RECONNECT` | LOW | ESP32 | Reconnexion MQTT | Log, flush buffer |
| `FLOOR_TRANSITION_FAIL` | HIGH | IoT Bridge | Timeout transition ascenseur | Notification opérateur |
| `LOCALIZATION_LOST` | HIGH | IoT Bridge | Score confiance AMCL < seuil | Notification, PAUSE_MISSION |
| `CONNECTIVITY_LOST` | HIGH | Broker (Will) | Déconnexion inopinée MQTT | Notification, timer watchdog |
| `EMERGENCY_STOP` | CRITICAL | Commande ou capteur | Bouton d'arrêt ou détection collision | Arrêt moteurs, log |

### 8.3 Machine d'états du robot (côté IoT)

```
                    ┌─────────────────┐
                    │    OFFLINE      │
                    │  (Will Message) │
                    └────────┬────────┘
                             │ Connexion MQTT
                             ▼
                    ┌─────────────────┐
                    │     IDLE        │◄──────────────────┐
                    │  (En attente)   │                   │
                    └────────┬────────┘                   │
                             │ Mission reçue              │ Mission terminée /
                             ▼                            │ Annulée
                    ┌─────────────────┐                   │
                    │  IN_MISSION     │───────────────────►│
                    │  (Navigation)   │                   │
                    └────────┬────────┘                   │
                             │                            │
              ┌──────────────┼───────────────┐            │
              │              │               │            │
              ▼              ▼               ▼            │
    ┌──────────────┐ ┌────────────┐ ┌──────────────┐     │
    │   PAUSED     │ │   STUCK    │ │  TRANSITION  │     │
    │  (Pause cmd) │ │ (Watchdog) │ │  (Ascenseur) │     │
    └──────┬───────┘ └─────┬──────┘ └──────┬───────┘     │
           │               │               │             │
           │ RESUME        │ Résolu /      │ Terminée    │
           │               │ Manual cmd    │             │
           └───────────────┴───────────────┘             │
                           │                             │
                           └─────────────────────────────┘
```

### 8.4 Mécanisme de watchdog UART (ESP32 → ROS 2)

Si l'ESP32-H2 ne reçoit plus de trames UART depuis la SBC ROS 2 pendant un délai configurable (défaut : 10 secondes), il :
1. Publie une alerte `UART_TIMEOUT` sur MQTT
2. Attend un délai de grâce (30s) pour une reprise automatique
3. Si toujours aucune trame : publie `EMERGENCY_STOP` et journalise

---

## 9. Contraintes techniques

### 9.1 Contraintes de latence

| Segment | Latence maximale cible | Latence maximale absolue |
|---------|----------------------|--------------------------|
| UART ROS 2 → ESP32-H2 | < 5 ms | < 20 ms |
| ESP32-H2 → Broker MQTT | < 50 ms (LAN) | < 200 ms (WAN) |
| Broker → Backend Node.js | < 10 ms | < 50 ms |
| Backend → Dashboard WebSocket | < 20 ms | < 100 ms |
| **Total end-to-end** | **< 100 ms** | **< 400 ms** |

### 9.2 Contraintes de bande passante

| Flux | Volume estimé | Calcul |
|------|--------------|--------|
| Télémétrie principale (2 Hz) | ~2 KB/s par robot | 1 KB × 2 msg/s |
| Vitesse (5 Hz) | ~0.5 KB/s | 100 B × 5 msg/s |
| Diagnostics (0.1 Hz) | ~0.05 KB/s | 500 B × 0.1 msg/s |
| **Total par robot** | **~2.5 KB/s** | — |
| **10 robots** | **~25 KB/s** | ~200 KB/s avec overhead MQTT |

### 9.3 Contraintes de disponibilité

| Composant | Disponibilité cible | MTTR cible |
|-----------|---------------------|------------|
| MQTT Broker | 99.9% (≤ 8.7h downtime/an) | < 5 min |
| Backend Node.js | 99.5% | < 15 min |
| Connectivité WiFi robot | 95% (zones de signal) | Auto-reconnexion |
| ESP32-H2 | 99.99% (embarqué) | Watchdog HW |

### 9.4 Contraintes de l'ESP32-H2

| Ressource | Budget alloué | Marge |
|-----------|--------------|-------|
| RAM totale | 320 KB | — |
| RAM tâche UART | 4 KB stack | — |
| RAM tâche MQTT | 8 KB stack | — |
| RAM tâche Watchdog | 2 KB stack | — |
| NVS buffer messages | 50 KB | ~100 msg de 500B |
| CPU moyen | < 40% | Pic < 80% |

### 9.5 Contraintes de format

| Paramètre | Valeur |
|-----------|--------|
| Encodage UART | UTF-8, délimiteur `\n` (LF) |
| Débit UART | 115200 baud (configurable jusqu'à 921600) |
| Taille max message UART | 2048 octets |
| Taille max payload MQTT | 256 MB (limite broker, pratique < 8 KB) |
| Horodatage | Unix timestamp en millisecondes (UTC) |
| Coordonnées | Float 64 bits, précision centimétrique |
| Unités | SI exclusivement (m, m/s, rad, V, A) |

---

## 10. Sécurité et fiabilité

### 10.1 Authentification et contrôle d'accès

#### Niveau ESP32-H2 → Broker MQTT

| Mécanisme | Implémentation |
|-----------|---------------|
| Authentification | Username + Password uniques par robot |
| Chiffrement transport | TLS 1.3 obligatoire (port 8883) |
| Certificat client | Certificat X.509 dédié par robot (mutual TLS) |
| ACL MQTT | Chaque robot ne peut publier/souscrire que sur ses topics (`robot/{son_id}/*`) |

#### Niveau Backend → Broker MQTT

| Mécanisme | Implémentation |
|-----------|---------------|
| Authentification | Service account dédié |
| ACL | Lecture sur `robot/+/#`, publication sur `robot/+/cmd/#` |
| Réseau | Broker en réseau privé, accès backend uniquement |

#### Niveau Utilisateur → Dashboard

| Mécanisme | Implémentation |
|-----------|---------------|
| Authentification | JWT (access token 15min + refresh token 7j) |
| Autorisation | RBAC (Roles : Viewer, Operator, Admin) |
| Transport | HTTPS + WSS uniquement |
| Rate limiting | 100 req/min par utilisateur sur l'API REST |

### 10.2 Matrice des permissions par rôle

| Action | Viewer | Operator | Admin |
|--------|--------|----------|-------|
| Voir télémétrie | ✅ | ✅ | ✅ |
| Voir alertes | ✅ | ✅ | ✅ |
| Voir historique | ✅ | ✅ | ✅ |
| Envoyer PAUSE / RESUME | ❌ | ✅ | ✅ |
| Envoyer STOP_EMERGENCY | ❌ | ✅ | ✅ |
| Créer missions | ❌ | ✅ | ✅ |
| Configurer robots | ❌ | ❌ | ✅ |
| Gérer utilisateurs | ❌ | ❌ | ✅ |
| Accès logs système | ❌ | ❌ | ✅ |

### 10.3 Intégrité des données

| Mécanisme | Description |
|-----------|-------------|
| Validation schéma JSON | Vérification à la réception (Zod côté backend, cJSON côté ESP32) |
| Numéro de séquence | Chaque trame UART inclut un champ `seq` incrémental pour détection de pertes |
| Checksums UART | CRC8 ou CRC16 optionnel sur trames critiques (commandes) |
| Idempotence commandes | Chaque commande porte un `request_id` unique pour dédoublonnage |
| Timestamps monotones | Validation côté backend (rejet si timestamp < dernière valeur - 5s) |

### 10.4 Fiabilité des communications

| Mesure | Détail |
|--------|--------|
| QoS MQTT adapté | Télémétrie : QoS 1 / Commandes : QoS 2 / Diagnostics : QoS 0 |
| Persistent session | Backend conserve session active (clean_session = false) |
| Will Message | Alerte automatique en cas de déconnexion inopinée |
| Buffer NVS ESP32 | Stockage local en cas de perte WiFi (100 messages) |
| Reconnexion automatique | Backoff exponentiel WiFi + MQTT (max 5 min) |
| Heartbeat MQTT | KEEPALIVE = 60s (broker déconnecte après 90s sans ping) |

### 10.5 Mise à jour firmware OTA (Over-The-Air)

Le firmware ESP32-H2 doit supporter les mises à jour OTA sécurisées :

```
┌─────────────────────────────────────────────────────┐
│                 OTA Update Flow                      │
│                                                      │
│  Backend ──MQTT cmd──► ESP32-H2                     │
│  {cmd: "OTA_UPDATE", url: "https://...", sha256: .} │
│                          │                           │
│                          │ 1. Vérification signature │
│                          │ 2. Téléchargement HTTPS   │
│                          │ 3. Vérification SHA-256   │
│                          │ 4. Flash partition B      │
│                          │ 5. Reboot sur partition B │
│                          │ 6. ACK MQTT + status OK   │
│                          │    (ou rollback auto si   │
│                          │     boot échoue)          │
└─────────────────────────────────────────────────────┘
```

---

## 11. Scalabilité multi-robots

### 11.1 Architecture de la flotte

Le système IoT est conçu dès sa conception pour gérer **N robots simultanément** (cible initiale : 10 robots, extensible à 50+).

```
                         ┌─────────────────────────────────┐
                         │        MQTT Broker               │
                         │   (Cluster EMQX ou Mosquitto)    │
                         └──────────────┬──────────────────┘
                                        │
              ┌───────────┬─────────────┼─────────────┬───────────┐
              │           │             │             │           │
         robot_01     robot_02     robot_03     robot_04     robot_N
              │           │             │             │           │
              └───────────┴─────────────┼─────────────┴───────────┘
                                        │
                         ┌──────────────▼──────────────────┐
                         │      Backend Node.js             │
                         │   (Workers + Message Queue)      │
                         │   ┌────────┐ ┌────────────────┐  │
                         │   │ Robot  │ │  Fleet Manager │  │
                         │   │ State  │ │  (agrégation)  │  │
                         │   │ Cache  │ └────────────────┘  │
                         │   │(Redis) │                     │
                         │   └────────┘                     │
                         └──────────────┬──────────────────┘
                                        │
                         ┌──────────────▼──────────────────┐
                         │      React Dashboard             │
                         │   Vue flotte + Vue robot unique  │
                         └─────────────────────────────────┘
```

### 11.2 Considérations d'échelle

| Paramètre | 1 robot | 10 robots | 50 robots |
|-----------|---------|-----------|-----------|
| Messages MQTT/s | ~12 | ~120 | ~600 |
| Bande passante | ~2.5 KB/s | ~25 KB/s | ~125 KB/s |
| Connexions broker | 1 + 1 backend | 10 + 1 backend | 50 + N backends |
| Charge DB (inserts/s) | ~10 | ~100 | ~500 |
| Cache Redis | Optionnel | Recommandé | Obligatoire |
| Broker clustering | Inutile | Optionnel | Requis |

### 11.3 Isolation par robot

Chaque robot possède :
- Un **identifiant unique** (`robot_id`) configuré à la fabrication en NVS ESP32
- Un **certificat TLS client** unique
- Un **compte MQTT** avec ACL restrictif
- Un **espace de topics** isolé `robot/{son_id}/*`
- Une **table dédiée** (ou partition) en base de données

### 11.4 Gestion des conflits d'accès aux ressources bâtiment

Le système IoT **notifie** le système de gestion de flotte (hors périmètre) des situations de potentiel conflit :
- Deux robots sur le même étage attendant l'ascenseur
- Mission destination identique simultanée
- Zone de l'ERP déclarée inaccessible

Ces décisions de résolution sont à la charge du **Fleet Management System** (hors périmètre IoT).

---

## 12. Diagrammes d'architecture

### 12.1 Diagramme de composants global

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                          ROBOT PHYSIQUE                                      ║
║                                                                              ║
║  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐                ║
║  │  LiDAR   │   │  Camera  │   │   IMU    │   │Encodeurs │                 ║
║  └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘                ║
║       └──────────────┴──────────────┴──────────────┘                        ║
║                              │                                               ║
║  ┌───────────────────────────▼──────────────────────────────────────────┐   ║
║  │                      SBC (Raspberry Pi 5 / Jetson)                   │   ║
║  │                                                                       │   ║
║  │  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  ┌─────────────┐  │   ║
║  │  │ Navigation2 │  │    AMCL     │  │  SLAM Gmpp │  │ MissionMgr  │  │   ║
║  │  │   (Nav2)    │  │Localization │  │  mapping   │  │             │  │   ║
║  │  └──────┬──────┘  └──────┬──────┘  └─────┬──────┘  └──────┬──────┘  │   ║
║  │         └────────────────┴────────────────┴────────────────┘          │   ║
║  │                                  │                                     │   ║
║  │                    ┌─────────────▼──────────────┐                     │   ║
║  │                    │      IoT Bridge Node        │                     │   ║
║  │                    │  (ROS 2 Python/C++ Node)    │                     │   ║
║  │                    │  - Agrège topics ROS 2      │                     │   ║
║  │                    │  - Sérialise en JSON        │                     │   ║
║  │                    │  - Écoute commandes UART    │                     │   ║
║  │                    └─────────────┬──────────────┘                     │   ║
║  └──────────────────────────────────┼──────────────────────────────────┘   ║
║                                     │ UART (Serial) 115200 baud             ║
║  ┌──────────────────────────────────▼──────────────────────────────────┐   ║
║  │                         ESP32-H2                                     │   ║
║  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────────┐  │   ║
║  │  │ UART Task  │  │ MQTT Task  │  │ Watchdog   │  │ NVS Buffer   │  │   ║
║  │  │            │  │   (TLS)    │  │   Task     │  │ (Offline)    │  │   ║
║  │  └────────────┘  └──────┬─────┘  └────────────┘  └──────────────┘  │   ║
║  └─────────────────────────┼────────────────────────────────────────┘   ║
╚═════════════════════════════╪════════════════════════════════════════════╝
                              │ WiFi 802.11 / MQTT over TLS 1.3
╔═════════════════════════════▼════════════════════════════════════════════╗
║                        INFRASTRUCTURE BACKEND                             ║
║                                                                           ║
║  ┌──────────────────────────────────────────────────────────────────┐   ║
║  │                    MQTT Broker (Mosquitto / EMQX)                │   ║
║  │   Port TLS: 8883  |  Port WSS: 8084  |  ACL: par robot_id       │   ║
║  └───────────────────────────┬──────────────────────────────────────┘   ║
║                               │                                           ║
║  ┌────────────────────────────▼─────────────────────────────────────┐   ║
║  │                    Node.js Backend                                │   ║
║  │  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌──────────────┐  │   ║
║  │  │ MQTT Sub  │  │ REST API  │  │ WebSocket │  │  Alert Eng.  │  │   ║
║  │  │  Handler  │  │  (Fastify)│  │ (Sock.io) │  │              │  │   ║
║  │  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └──────────────┘  │   ║
║  │        │              │               │                            │   ║
║  │  ┌─────▼──────────────▼───────────────▼────────────────────────┐ │   ║
║  │  │              TimescaleDB (PostgreSQL)                        │ │   ║
║  │  │  Tables: telemetry | alerts | missions | robots | floors     │ │   ║
║  │  └──────────────────────────────────────────────────────────────┘ │   ║
║  └────────────────────────────┬─────────────────────────────────────┘   ║
║                                │ WebSocket (WSS)                          ║
║  ┌─────────────────────────────▼────────────────────────────────────┐   ║
║  │                    React Dashboard                                │   ║
║  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────────┐  │   ║
║  │  │  MapView │  │ Status   │  │  Alerts  │  │  Command Panel  │  │   ║
║  │  │ (Leaflet)│  │  Panel   │  │   Feed   │  │                 │  │   ║
║  │  └──────────┘  └──────────┘  └──────────┘  └─────────────────┘  │   ║
║  └──────────────────────────────────────────────────────────────────┘   ║
╚══════════════════════════════════════════════════════════════════════════╝
```

### 12.2 Diagramme de séquence — Démarrage complet

```
ESP32-H2    WiFi Stack    MQTT Broker    Node.js Backend    ROS 2 Node
    │            │              │                │               │
    │ Boot       │              │                │               │
    │───────────►│              │                │               │
    │            │ Connect      │                │               │
    │            │─────────────►│                │               │
    │            │              │ ACK            │               │
    │            │◄─────────────│                │               │
    │ TLS Handshake + Auth      │                │               │
    │──────────────────────────►│                │               │
    │ Will Message configured   │                │               │
    │ Subscribe /cmd, /cmd/mission               │               │
    │ Publish /connection ONLINE (retained)      │               │
    │──────────────────────────►│                │               │
    │                           │──── DELIVER ──►│               │
    │                           │                │ Mark ONLINE   │
    │                           │                │ in DB         │
    │                           │                │               │ ROS 2 boot
    │                           │                │               │ Nav2 init
    │◄── UART first frame ──────────────────────────────────────│
    │ {type: "telemetry", ...}  │                │               │
    │ Watchdog reset            │                │               │
    │ Publish telemetry         │                │               │
    │──────────────────────────►│                │               │
    │                           │──── DELIVER ──►│               │
    │                           │                │ First state   │
    │                           │                │ in DB         │
    │                           │                │─── WS push ──►│ (Dashboard)
```

### 12.3 Structure des topics par étage

```
robot/robot_01/
├── telemetry              ← Agrégat principal
├── telemetry/
│   ├── pose               ← Position + orientation (retained)
│   ├── velocity           ← Vitesse
│   └── battery            ← Batterie (retained)
├── status                 ← État global (retained)
├── mission                ← Mission courante (retained)
├── floor                  ← Étage courant (retained)
├── diagnostics            ← Métriques système
├── connection             ← Online/Offline (retained + Will)
├── alerts                 ← Canal général alertes
│   ├── stuck              ← Robot bloqué
│   ├── battery_low        ← Batterie faible
│   ├── navigation_error   ← Erreur Nav2
│   ├── floor_transition   ← Changement d'étage
│   ├── uart_timeout       ← Perte UART
│   └── connectivity_lost  ← Perte WiFi
└── cmd/                   ← Commandes entrantes (QoS 2)
    ├── (general)          ← STOP, PAUSE, RESUME
    ├── mission            ← Commandes de mission
    └── config             ← Configuration distante
```

---

## 13. Critères d'acceptation

### 13.1 Tests fonctionnels obligatoires

| ID Test | Description | Critère de succès |
|---------|-------------|-------------------|
| TF-01 | Connexion MQTT ESP32-H2 | Connexion établie < 10s après boot |
| TF-02 | Transmission télémétrie | Données reçues en backend < 200ms |
| TF-03 | Affichage position dashboard | Position affichée < 500ms après mouvement |
| TF-04 | Détection robot bloqué | Alerte émise entre 5s et 7s après blocage |
| TF-05 | Envoi commande STOP | Commande exécutée < 1s après envoi dashboard |
| TF-06 | Transition ascenseur | Carte bascule automatiquement sur dashboard |
| TF-07 | Perte WiFi et recovery | Données bufferisées et renvoyées à reconnexion |
| TF-08 | Will Message | Alerte OFFLINE visible sur dashboard < 90s |
| TF-09 | OTA firmware ESP32 | Mise à jour réussie sans perte de supervision |
| TF-10 | Gestion multi-robots | 5 robots simultanés sans dégradation |

### 13.2 Tests de performance

| ID Test | Description | Critère de succès |
|---------|-------------|-------------------|
| TP-01 | Latence end-to-end | P95 < 200ms, P99 < 400ms |
| TP-02 | Charge broker 10 robots | < 5% CPU broker, 0 message perdu |
| TP-03 | Durée de session continue | 8h de fonctionnement sans redémarrage ESP32 |
| TP-04 | Volume historique | Requête 24h de données en < 2s |
| TP-05 | Reconnexion MQTT | Reconnexion automatique < 30s après perte |

### 13.3 Tests de sécurité

| ID Test | Description | Critère de succès |
|---------|-------------|-------------------|
| TS-01 | Authentification MQTT | Connexion refusée sans certificat valide |
| TS-02 | ACL topics | Robot 01 ne peut pas publier sur `robot/02/*` |
| TS-03 | HTTPS obligatoire | API REST inaccessible en HTTP |
| TS-04 | JWT expiration | Token expiré → 401 Unauthorized |
| TS-05 | Injection JSON | Payload malformé ignoré et loggé |
| TS-06 | RBAC | Viewer ne peut pas envoyer de commande (403) |

### 13.4 Tests de fiabilité

| ID Test | Description | Critère de succès |
|---------|-------------|-------------------|
| TR-01 | Uptime broker | 99.9% sur 30 jours consécutifs |
| TR-02 | Buffer NVS | Aucune donnée perdue après 2 min de perte WiFi |
| TR-03 | Watchdog UART | Alerte émise si ROS 2 silencieux 10s |
| TR-04 | Redémarrage ESP32 | Reconnexion automatique après power cycle |
| TR-05 | Cohérence données | Aucun gap > 5s dans historique télémétrie |

---

## 14. Évolutions futures possibles

### 14.1 Évolutions techniques à court terme (V1.1 — V1.2)

| Évolution | Description | Complexité |
|-----------|-------------|------------|
| Thread/Matter | Remplacer WiFi par Thread (protocole natif ESP32-H2) pour résilience mesh | Haute |
| Edge AI (ESP32) | Détection d'anomalies par modèle ML embarqué (TFLite Micro) | Haute |
| Compression messages | CBOR ou MessagePack pour réduire bande passante de 60% | Moyenne |
| Streaming vidéo | Flux caméra embarquée vers dashboard (RTSP / WebRTC) | Haute |
| Notifications Push | Alertes mobile (Firebase FCM) pour opérateurs | Faible |

### 14.2 Évolutions architecturales à moyen terme (V2.0)

| Évolution | Description | Impact |
|-----------|-------------|--------|
| Digital Twin | Jumeau numérique du robot (synchronisation 3D temps réel) | Fort |
| Fleet Analytics | Tableau de bord analytique (KPIs flotte, optimisation missions) | Moyen |
| Intégration ERP/GMAO | Connexion avec systèmes de gestion du bâtiment (API REST) | Moyen |
| Micro-services | Découplage backend en services indépendants (Docker/K8s) | Fort |
| Multi-building | Extension à plusieurs bâtiments avec routing inter-sites | Fort |

### 14.3 Intégrations tierces envisageables

| Système | Type d'intégration | Protocole |
|---------|--------------------|-----------|
| BMS (Building Mgmt) | Contrôle ascenseurs, portes automatiques | BACnet / Modbus / REST |
| Système de badges | Validation accès zones sécurisées | LDAP / REST |
| GMAO | Déclenchement tickets maintenance sur alerte | REST / Webhook |
| ERP Entrepôt | Synchronisation missions avec flux logistique | REST / gRPC |
| Supervision réseau | Intégration monitoring (Prometheus / Grafana) | Prometheus exporter |

---

## 15. Glossaire

| Terme | Définition |
|-------|------------|
| **ACL** | Access Control List — liste de règles d'accès aux topics MQTT |
| **AMCL** | Adaptive Monte Carlo Localization — algorithme de localisation probabiliste ROS 2 |
| **Broker** | Serveur MQTT jouant le rôle d'intermédiaire de messages |
| **ERP** | Établissement Recevant du Public |
| **ESP32-H2** | Microcontrôleur Espressif (RISC-V, Thread, Zigbee, BLE 5.2) |
| **FreeRTOS** | Système d'exploitation temps réel pour microcontrôleurs |
| **GMAO** | Gestion de Maintenance Assistée par Ordinateur |
| **IoT** | Internet of Things — Internet des objets |
| **JWT** | JSON Web Token — format standardisé de jeton d'authentification |
| **KEEPALIVE** | Paramètre MQTT définissant l'intervalle maximal sans communication |
| **Nav2** | Navigation2 — stack de navigation autonome pour ROS 2 |
| **NVS** | Non-Volatile Storage — mémoire flash persistante de l'ESP32 |
| **OTA** | Over-The-Air — mise à jour de firmware à distance |
| **QoS** | Quality of Service — niveau de garantie de livraison MQTT (0, 1 ou 2) |
| **RBAC** | Role-Based Access Control — contrôle d'accès basé sur les rôles |
| **Retained message** | Message MQTT conservé par le broker et livré immédiatement aux nouveaux souscripteurs |
| **ROS 2** | Robot Operating System 2 — framework de développement robotique |
| **SBC** | Single Board Computer (ex. : Raspberry Pi, Jetson) |
| **SLAM** | Simultaneous Localization And Mapping — cartographie et localisation simultanées |
| **TLS** | Transport Layer Security — protocole de chiffrement des communications |
| **UART** | Universal Asynchronous Receiver-Transmitter — liaison série asynchrone |
| **Will Message** | Message MQTT automatiquement envoyé par le broker si un client se déconnecte inopinément |
| **Waypoint** | Point de passage prédéfini sur la carte du bâtiment |
| **WebSocket** | Protocole de communication bidirectionnelle temps réel sur HTTP |

---

## Annexe A — Configuration matérielle de référence

### Robot de référence

| Composant | Spécification |
|-----------|--------------|
| SBC | Raspberry Pi 5 (8 GB RAM) ou NVIDIA Jetson Orin Nano |
| LiDAR | RPLIDAR A3 ou Sick TiM571 |
| Caméra profondeur | Intel RealSense D435i |
| IMU | BNO055 ou MPU-6050 |
| Châssis | Differential drive ou omnidirectionnel |
| Batterie | LiPo 24V 20Ah (autonomie cible : 4h) |
| WiFi | Module M.2 WiFi 6 (AX200) |
| MCU IoT | ESP32-H2 DevKit ou ESP32-S3 (pour WiFi natif) |

### Câblage UART

```
Raspberry Pi 5          ESP32-H2
    GPIO14 (TX) ────────► RXD0
    GPIO15 (RX) ◄──────── TXD0
    GND ─────────────────── GND
    (Niveaux 3.3V — compatibles directs)
```

---

## Annexe B — Variables de configuration ESP32-H2

| Variable | Type | Valeur par défaut | Description |
|----------|------|-------------------|-------------|
| `ROBOT_ID` | string | `"robot_01"` | Identifiant unique robot |
| `MQTT_BROKER_HOST` | string | `"mqtt.example.com"` | Adresse du broker |
| `MQTT_BROKER_PORT` | int | `8883` | Port TLS MQTT |
| `MQTT_KEEPALIVE_S` | int | `60` | Keepalive MQTT |
| `UART_BAUD_RATE` | int | `115200` | Débit série |
| `UART_TIMEOUT_MS` | int | `10000` | Timeout UART watchdog |
| `STUCK_THRESHOLD_S` | float | `5.0` | Durée avant alerte blocage |
| `V_CMD_MIN_MS` | float | `0.05` | Seuil vitesse commandée |
| `V_REAL_MAX_MS` | float | `0.02` | Seuil quasi-immobilité |
| `NVS_BUFFER_MAX` | int | `100` | Taille max buffer NVS |
| `WIFI_RECONNECT_MAX_S` | int | `300` | Délai max reconnexion WiFi |
| `TELEMETRY_FREQ_HZ` | float | `2.0` | Fréquence publication MQTT |
| `BATTERY_LOW_PCT` | int | `20` | Seuil alerte batterie faible |
| `BATTERY_CRITICAL_PCT` | int | `10` | Seuil alerte batterie critique |

---

*Document généré pour le projet Robot Mobile Autonome ERP — Couche IoT uniquement.*  
*Version 1.0.0 — Révision : Ingénierie Robotique & IoT*  
*Ce document doit être placé dans `docs/iot/CDC_IoT.md` du dépôt GitHub du projet.*