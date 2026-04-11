# WebSocket Robot -> Site

## Objectif

Le WebSocket sert de lien temps reel entre le robot et le site.

Dans cette version :

- le robot envoie ses evenements au serveur WebSocket
- le serveur WebSocket met a jour la base partagee avec l'API
- le serveur WebSocket diffuse ces evenements au frontend

## Adresse par defaut

```text
ws://localhost:8765
```

## Identification

Le premier message doit etre :

```json
{
  "type": "identify",
  "client_type": "robot",
  "robot_id": "robot-1"
}
```
ou
```json
{
  "type": "identify",
  "client_type": "dashboard"
}
```

## Evenements robot supportes

### Heartbeat

```json
{
  "type": "robot.heartbeat",
  "robot_id": "robot-1",
  "timestamp": "2026-04-11T10:15:00Z"
}
```

### Position

```json
{
  "type": "robot.position_updated",
  "robot_id": "robot-1",
  "mission_id": 12,
  "x": 12.4,
  "y": 7.8,
  "timestamp": "2026-04-11T10:15:01Z"
}
```

Cet evenement est insere dans `robot_logs`.

### Statut de mission

```json
{
  "type": "mission.status_updated",
  "robot_id": "robot-1",
  "mission_id": 12,
  "status": "NAVIGATING_TO_PICKUP",
  "timestamp": "2026-04-11T10:15:04Z"
}
```

Cet evenement met a jour la table `missions`.

## Evenements diffuses au frontend

- `server.ack`
- `server.error`
- `robot.connected`
- `robot.disconnected`
- `robot.heartbeat`
- `robot.position_updated`
- `mission.status_updated`
