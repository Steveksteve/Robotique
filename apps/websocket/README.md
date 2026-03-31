# WebSocket Module

Ce dossier regroupe le socle WebSocket du projet :

- `server/` : relais WebSocket central
- `dashboard/` : page minimale d'ecoute live

Le robot reste dans `apps/robot`, mais il se connecte a ce module.

## Demarrage local

Depuis la racine du repo :

```bash
docker compose -f docker-compose.realtime.yml up --build -d
```

Ensuite :

- dashboard : ouvrez `apps/websocket/dashboard/live.html`
- robot : `python apps/robot/client.py`
