# Lancer les tests RAA

Ce guide explique comment lancer les tests unitaires et d integration en local.

## Prerequis

- Docker
- Docker Compose
- Python 3

## Lancer toute la suite comme la CI

### Linux / macOS / WSL

```bash
./scripts/run_ci_local.sh
```

### Windows PowerShell

```powershell
.\scripts\run_ci_local.ps1
```

Ces scripts :

- demarrent la stack de test
- attendent que l API et le front soient disponibles
- lancent les tests unitaires IoT
- lancent les tests d integration
- nettoient les conteneurs a la fin

## Lancer les tests unitares IoT seulement

```bash
python -m pytest tests/unit/iot -q
```

## Lancer les tests d integration seulement

```bash
python -m pip install -r tests/integration/requirements-test.txt
API_BASE=http://localhost:8000 \
WS_URL=ws://localhost:8765 \
WEB_BASE=http://localhost:8080 \
python -m pytest tests/integration/ -q
```

## Lancer manuellement la stack de test

Si tu veux garder la stack ouverte avant de lancer les tests :

```bash
docker compose -f docker-compose.test.yml up --build -d
```

Verifications utiles :

```bash
curl http://localhost:8000/health
curl http://localhost:8080/
```

Arret :

```bash
docker compose -f docker-compose.test.yml down -v
```

## Rapport

Les scripts de test generent des rapports JUnit dans `reports/`.
