# Exécution locale du pipeline d'intégration

Ce document explique comment lancer l'environnement de test localement et exécuter les tests d'intégration.

Prérequis
- Docker & Docker Compose installés
- Python 3 + pytest (pour exécuter les tests localement)

Étapes

1. Construire et démarrer les services de test

```bash
docker compose -f docker-compose.test.yml up --build -d
```

2. Vérifier que l'API est disponible

```bash
curl -sS http://localhost:8000/ || echo "API non disponible"
```

3. Lancer les tests d'intégration (depuis la racine du repo)

```bash
pip install -r requirements-test.txt  # si vous avez un fichier requirements, sinon pip install pytest requests
pytest tests/integration/ -q
```

4. Nettoyer

```bash
docker compose -f docker-compose.test.yml down -v
```

## Test local du WebSocket

Pour tester le flux robot -> site en local :

1. Demarrer l'API, la base et le relais WebSocket

```bash
docker compose -f docker-compose.realtime.yml up --build -d
```

2. Ouvrir le dashboard de debug dans le navigateur

```text
apps/websocket/dashboard/live.html
```

3. Lancer le client robot

```bash
python apps/robot/client.py
```

4. Ouvrir le fichier HTML dans le navigateur puis verifier que les evenements `robot.heartbeat`, `robot.position_updated` et `mission.status_updated` apparaissent dans la page

5. Nettoyer

```bash
docker compose -f docker-compose.realtime.yml down -v
```

Dépannage
- Si la DB ne démarre pas, consultez les logs : `docker compose logs db`
- Si l'API renvoie des erreurs, consulter : `docker compose logs api`


Scripts fournis
- `scripts/run_ci_local.sh` : script bash pour Linux / macOS / WSL
- `scripts/run_ci_local.ps1` : script PowerShell pour Windows

Prérequis
- Docker & Docker Compose installés
- Python 3 et `pytest` pour exécuter les tests

Usage (Linux / macOS / WSL)

```bash
./scripts/run_ci_local.sh
```

Usage (Windows PowerShell)

```powershell
.\scripts\run_ci_local.ps1
```

Que font ces scripts ?
- Construisent et démarrent les services définis dans `docker-compose.test.yml`.
- Attendent que l'API réponde (`http://localhost:8000/`).
- Exécutent les tests d'intégration (pytest).
- Collectent le rapport JUnit dans `reports/junit.xml` et démontent les services.

