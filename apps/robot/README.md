# M3 Pro Teacher Workspace - Docker Dashboard

> Cette page décrit le workspace robot historique. Pour le workflow final, les statuts de mission et l’état réel des essais, consulter le README à la racine, `docs/STATE_MACHINE.md` et `docs/ROBOT_FINAL_PIPELINE_STATUS.md`.


**Status**:  Fonctionnel en environnement de test | **Dernière mise à jour** : 22 mai 2026

---

##  Démarrage Rapide (30 secondes)

```bash
cd m3pro_teacher_ws

# Lancer les services Docker
docker-compose up -d

# Ouvrir le dashboard
open http://localhost:8080

# Voir l'état
docker-compose ps
```

---

##  Dashboard Web

**URL**: http://localhost:8080

###  Features
-  Map SLAM interactive (click pour naviguer)
-  Camera stream en direct (3 modes)
-  Robot state (position, velocités)
-  Indicateur connexion ROS2
-  Responsive (mobile + desktop)

---

## Architecture Docker

4 services orchestrés:

```
ros_core      → ROS2 daemon
   ↓
rosbridge     → WebSocket (port 9090)
   ↓
dashboard     → HTTP Server (port 8080)

+ m3pro_teacher_build → Build workspace
```

**Healthchecks**: Tous les services ont des vérifications d'état automatiques.

---

##  Documentation

| Document | Contenu |
|----------|---------|
| **DOCKER_SETUP.md** | Guide Docker complet |
| **DOCKER_IMPROVEMENTS.md** | Résumé des améliorations |
| **PROJECT_STATUS.md** | État global du projet |
| **EXECUTION_GUIDE.md** | Phases A-G d'exécution |
| **QUICK_REFERENCE.md** | Params de configuration |
| **TECHNICAL_REFERENCE.md** | Architecture système |

---

##  Commandes Utiles

### Avec le script launcher

```bash
bash docker_launcher.sh up           # Build + lance
bash docker_launcher.sh logs         # Voir les logs
bash docker_launcher.sh status       # État services
bash docker_launcher.sh test-dashboard  # Tester
bash docker_launcher.sh down         # Arrêter
```

### Avec docker-compose directement

```bash
docker-compose up -d                 # Lancer
docker-compose ps                    # État
docker-compose logs -f               # Logs temps réel
docker-compose down                  # Arrêter
```

### Test rapide

```bash
bash test_dashboard.sh              # Tests complets
```

---

##  Fichiers Clés Modifiés/Créés

```
  Dockerfile                   - Amélioré (http-server)
  docker-compose.yml           - Version 3.9, 4 services
 .env                          - Variables d'environnement
 DOCKER_SETUP.md               - Guide complet
 DOCKER_IMPROVEMENTS.md        - Résumé améliorations
 PROJECT_STATUS.md             - État projet
 docker_launcher.sh            - Script de lancement
 test_dashboard.sh             - Script de test
 README.md                      - Ce fichier
```

---

##  Accès Services

| Service | Port | URL |
|---------|------|-----|
| Dashboard | 8080 | http://localhost:8080 |
| RosBridge | 9090 | ws://localhost:9090 |

**Sur le robot** (Jetson 10.10.221.123):
- Dashboard: http://10.10.221.123:8080
- RosBridge: ws://10.10.221.123:9090

---

## [OK] Checklist Avant Démarrage

- [ ] Docker installé
- [ ] Ports 8080, 9090 libres
- [ ] Dans le bon répertoire (`m3pro_teacher_ws`)
- [ ] Fichier `.env` présent
- [ ] `docker-compose.yml` à jour

---

##  Vérifier que Ça Marche

```bash
# Test 1: Services en route
docker-compose ps
# → Tous doivent montrer "Up (healthy)"

# Test 2: Dashboard accessible
curl http://localhost:8080
# → HTTP 200

# Test 3: RosBridge connecté
python3 << 'EOF'
import websocket
ws = websocket.create_connection("ws://localhost:9090")
ws.close()
print("OK")
EOF
# → "OK" s'affiche

# Ou utiliser le script intégré
bash test_dashboard.sh
```

---

## Attention : Dépannage

### Services ne démarrent pas
```bash
docker-compose build
docker-compose up -d
docker-compose logs
```

### Dashboard ne charge pas
```bash
curl -v http://localhost:8080
docker-compose logs dashboard
```

### RosBridge déconnecté
```bash
docker-compose restart rosbridge
docker-compose logs -f rosbridge
```

### Tout réinitialiser
```bash
docker-compose down -v
docker-compose up -d
```

---

##  Exécution Robot Complet (40 min)

7 phases d'apprentissage:

| Phase | Objectif | Temps | État |
|-------|----------|-------|--------|
| A | SLAM - Build map | 10min | [OK] |
| B | Nav2 - Navigate | 5min | [OK] |
| C | Web - Dashboard | 2min | [OK] |
| D | Vision - Detect | 3min | [OK] |
| E | Pick - Grasp | 5min | [OK] |
| F | Integration | 10min | [OK] |
| G | Cleanup | 2min | [OK] |

Voir `EXECUTION_GUIDE.md` pour les détails.

---

##  Sur le Robot Jetson

```bash
# 1. Depuis ton PC
ssh jetson@10.10.221.123 'bash /home/jetson/start_agent.sh'

# 2. Déployer le workspace
CONTAINER=infallible_kare ./scripts/deploy_workspace_to_robot.sh 10.10.221.123

# 3. Sur le robot
docker-compose up -d

# 4. Accéder
# http://10.10.221.123:8080
```

---

##  Technologies

- **ROS2 Humble** - Middleware robotique
- **Docker** - Containerization
- **WebSocket** - Communication temps réel
- **HTML5 + JavaScript** - Web UI
- **RosLib.js** - ROS client JS

---

##  Liens Rapides

- **Dashboard**: http://localhost:8080
-  **Docs Complètes**: DOCKER_SETUP.md
-  **Guide Exécution**: EXECUTION_GUIDE.md
- **Référence Technique**: TECHNICAL_REFERENCE.md
-  **État Projet**: PROJECT_STATUS.md

---

##  Tips

- Édite `.env` pour changer les ports
- Utilise `docker-compose logs -f SERVICE` pour debug
- Le script `docker_launcher.sh` a plus de 10 commandes pratiques
- Les healthchecks redémarrent auto les services défaillants

---

##  Version

**v1.0** - May 22, 2026
- [OK] Docker Dashboard complet
- [OK] Architecture 4-service
- [OK] Documentation complète
- [OK] Scripts de test

---

##  Ready to Go!

```bash
docker-compose up -d && echo "[OK] Dashboard démarré!" && echo "-> http://localhost:8080"
```

---

* Robot | M3Pro Teacher Workspace*
