# Docker Setup Guide - M3 Pro Teacher Workspace

##  Vue d'ensemble

Le setup Docker inclut plusieurs services coordonnés pour le robot M3 Pro :

```
┌─────────────────────────────────────────┐
│     Docker Compose Network               │
├─────────────────────────────────────────┤
│                                         │
│   ros_core (ROS2 Daemon)              │
│     └── Gestionnaire DDS/ROS2 global   │
│                                         │
│   rosbridge (Port 9090)               │
│     └── WebSocket ROS communication    │
│         └── Dépend de: ros_core        │
│                                         │
│   dashboard (Port 8080)               │
│     └── Web HTTP Server (index.html)   │
│         └── Dépend de: rosbridge       │
│                                         │
│    m3pro_teacher_build (Build)       │
│     └── Construit le workspace         │
│                                         │
└─────────────────────────────────────────┘
```

---

##  Démarrage Rapide

### Option 1 : Build et lancer tous les services

```bash
cd /mnt/c/hetic/aaaa/m3pro_teacher_ws

# Build l'image
docker-compose build

# Lance tous les services
docker-compose up -d

# Vérifie l'état
docker-compose ps

# Logs en temps réel
docker-compose logs -f

# Accès au dashboard
# - Web: http://localhost:8080
# - RosBridge WebSocket: ws://localhost:9090
```

### Option 2 : Lancer le build uniquement (local test)

```bash
docker-compose run --build --rm m3pro_teacher_build
```

---

##  Accès aux Services

| Service | Port | URL | Description |
|---------|------|-----|-------------|
| **Dashboard** | 8080 | `http://localhost:8080` | Web UI du robot |
| **RosBridge** | 9090 | `ws://localhost:9090` | WebSocket ROS communication |

---

##  Commandes Utiles

### Vérifier les services

```bash
# État de tous les services
docker-compose ps

# Logs d'un service spécifique
docker-compose logs -f rosbridge
docker-compose logs -f dashboard
```

### Entrer dans un container

```bash
# Shell dans le container ros_core
docker-compose exec ros_core bash

# Shell dans le container rosbridge
docker-compose exec rosbridge bash

# Shell dans le container dashboard
docker-compose exec dashboard bash
```

### Arrêter / Redémarrer

```bash
# Arrêter tous les services
docker-compose down

# Arrêter un service spécifique et le relancer
docker-compose restart rosbridge

# Redémarrer tous les services
docker-compose down && docker-compose up -d
```

---

##  Test de Connectivité

### Via RosBridge

```bash
# Depuis n'importe quel terminal avec Python
python3 << 'EOF'
import websocket
import json

try:
    ws = websocket.create_connection("ws://localhost:9090")
    ws.send(json.dumps({"op": "service_type", "service": "/rosapi/services"}))
    result = ws.recv()
    print("[OK] RosBridge connected:", result[:50] + "...")
    ws.close()
except Exception as e:
    print("[ERREUR] RosBridge error:", e)
EOF
```

### Via Dashboard

Ouvre http://localhost:8080 dans ton navigateur. Tu dois voir :
- Indicateur "CONNECTED" en vert en haut à gauche
- Panneau de la caméra (en attente de stream)
- Carte du robot
- État du robot

---

##  Configuration Réseau

Par défaut, tous les services sont sur le réseau `m3pro_network` (bridge):

```bash
# Voir le réseau
docker network ls | grep m3pro
docker network inspect m3pro_network
```

### Pour connecter depuis le PC (non-Docker)

Si tu veux accéder aux services depuis ton PC hôte (pas dans Docker):
- Dashboard: `http://localhost:8080`
- RosBridge: `ws://localhost:9090`

Si tu veux connecter depuis le robot Jetson:
- Remplace `localhost` par l'IP du PC (ex: `10.10.221.XXX`)

---

##  Personnalisations Courantes

### Ajouter un nouveau service ROS2

Édite `docker-compose.yml`:

```yaml
  mon_node:
    image: m3pro_teacher_ws:humble
    container_name: m3pro_teacher_mon_node
    environment:
      ROS_DOMAIN_ID: "30"
      FASTDDS_BUILTIN_TRANSPORTS: UDPv4
    command: >
      bash -lc "source /opt/ros/humble/setup.bash
      && source /root/m3pro_teacher_ws/install/setup.bash
      && ros2 launch m3pro_teacher_demos mon_demo.launch.py"
    networks:
      - m3pro_network
    depends_on:
      - ros_core
    restart: unless-stopped
```

Puis relance:
```bash
docker-compose up -d
```

### Changer le port du dashboard

Dans `docker-compose.yml`, section `dashboard`:

```yaml
ports:
  - "8000:8080"  # Port externe 8000 → port interne 8080
```

### Activer les logs GPU (si tu as NVIDIA)

Dans le Dockerfile, après `FROM ros:humble-ros-base`:

```dockerfile
RUN apt-get install -y nvidia-container-runtime
```

Et dans `docker-compose.yml`:

```yaml
services:
  mon_service:
    runtime: nvidia  # Active GPU
```

---

## Dépannage

### RosBridge ne se connecte pas

```bash
# Vérifier les logs
docker-compose logs rosbridge

# Vérifier que ros_core est bien lancé
docker-compose ps ros_core

# Relancer
docker-compose restart rosbridge
```

### Dashboard ne charge pas

```bash
# Vérifier le service
docker-compose logs dashboard

# Vérifier le port
curl http://localhost:8080

# Vérifier la connexion WebSocket
docker-compose exec dashboard bash
# Puis depuis le shell:
# python3 -c "from roslib.message import Message; print('OK')"
```

### Problème de compilation

```bash
# Supprimer les caches et reconstruire
docker-compose build --no-cache

# Ou nettoyer complètement
docker-compose down
docker volume prune -f
docker-compose up -d
```

---

##  Fichiers Modifiés

- `Dockerfile` : Ajout de `python3-http-server`
- `docker-compose.yml` : Ajout de 3 services (ros_core, rosbridge, dashboard)

---

##  Étapes Suivantes

1. **Build** : `docker-compose build`
2. **Lancer** : `docker-compose up -d`
3. **Accéder** : `http://localhost:8080`
4. **Tester** : Vérifier les logs avec `docker-compose logs -f`
5. **Déployer** : Configurer les variables d'environnement pour le robot Jetson

---

##  Sur le Robot Jetson

Pour déployer sur le robot et utiliser les services Docker:

```bash
# 1. Depuis ton PC, copier le workspace au robot
ssh jetson@10.10.221.123 'bash /home/jetson/start_agent.sh'

# 2. Lancer les services Docker sur le robot
docker-compose up -d

# 3. Accéder au dashboard
# http://10.10.221.123:8080
```

**Variables d'environnement importantes** :
- `ROS_DOMAIN_ID=30` : Pour que les containers communiquent avec le robot
- `FASTDDS_BUILTIN_TRANSPORTS=UDPv4` : Protocole réseau

---
