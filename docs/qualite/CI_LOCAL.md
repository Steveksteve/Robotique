# Exécution locale de la CI

Prérequis : Docker, Docker Compose et Python 3.

## Full stack de test

```bash
docker compose -f docker-compose.test.yml up --build -d
```

Vérifications :

```bash
curl http://localhost:8000/health
curl http://localhost:8080/
```

Tests :

```bash
python -m pip install -r tests/integration/requirements-test.txt
API_BASE=http://localhost:8000 \
WS_URL=ws://localhost:8765 \
WEB_BASE=http://localhost:8080 \
python -m pytest tests/integration/ -q
```

Nettoyage :

```bash
docker compose -f docker-compose.test.yml down -v
```

## Scripts fournis

Linux / macOS / WSL :

```bash
./scripts/run_ci_local.sh
```

Windows PowerShell :

```powershell
.\scripts\run_ci_local.ps1
```
