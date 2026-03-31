# WebSocket Robot -> Site

## Objectif

Mettre en place un flux temps reel entre le robot et l'interface web sans passer par du polling permanent.

Architecture retenue :

- le robot emet des evenements temps reel
- un serveur WebSocket central les recoit et les redistribue
- le site se connecte au meme serveur pour afficher les mises a jour en live

## Pourquoi cette architecture

- le robot et le site sont decouples
- plusieurs clients web peuvent ecouter en meme temps
- le backend REST garde la logique metier et la persistance
- le WebSocket reste concentre sur le transport temps reel

## Types de clients

- `robot` : producteur d'evenements
- `dashboard` : consommateur d'evenements

Chaque client ouvre une connexion sur le serveur WebSocket puis envoie un message `identify`.

## Message d'identification

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

## Evenements emis par le robot

### Heartbeat

```json
{
  "type": "robot.heartbeat",
  "robot_id": "robot-1",
  "timestamp": "2026-03-31T10:15:00Z"
}
```

### Position

```json
{
  "type": "robot.position_updated",
  "robot_id": "robot-1",
  "x": 12.4,
  "y": 7.8,
  "battery": 83,
  "timestamp": "2026-03-31T10:15:01Z"
}
```

### Statut de mission

```json
{
  "type": "mission.status_updated",
  "robot_id": "robot-1",
  "mission_id": 12,
  "status": "NAVIGATING",
  "timestamp": "2026-03-31T10:15:04Z"
}
```

## Evenements emis par le serveur

Le serveur relaye les evenements robot aux dashboards et emet aussi :

```json
{
  "type": "server.ack",
  "message": "identified",
  "client_type": "robot"
}
```

```json
{
  "type": "server.robot_connected",
  "robot_id": "robot-1",
  "timestamp": "2026-03-31T10:15:00Z"
}
```

```json
{
  "type": "server.robot_disconnected",
  "robot_id": "robot-1",
  "timestamp": "2026-03-31T10:18:12Z"
}
```

## MVP recommande

1. demarrer le serveur WebSocket
2. faire emettre `identify`, `robot.heartbeat`, `mission.status_updated`
3. connecter une page dashboard simple
4. verifier la reception en live

## Evolutions ensuite

- authentification par token
- persistance des logs robot
- replay des derniers evenements aux nouveaux dashboards
- rooms par robot ou par mission
- integration CI avec un vrai `WS_URL`


Les fichiers du module sont regroupes dans pps/websocket/.
