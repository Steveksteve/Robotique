# Protocole WebSocket RAA

Adresse locale :

```text
ws://localhost:8765
```

Depuis le front Docker/Nginx :

```text
/ws
```

## Identification

Dashboard :

```json
{
  "type": "identify",
  "client_type": "dashboard"
}
```

Robot :

```json
{
  "type": "identify",
  "client_type": "robot",
  "robot_id": "raa-robot-01"
}
```

Réponse serveur :

```json
{
  "type": "server.ack",
  "message": "identified"
}
```

## Dashboard → serveur

Affecter une mission :

```json
{
  "type": "mission:assign",
  "mission_id": 12,
  "robot_id": "raa-robot-01"
}
```

Arrêt d’urgence :

```json
{
  "type": "robot:emergency_stop",
  "mission_id": 12,
  "reason": "Arrêt demandé depuis le dashboard"
}
```

## Serveur → robot

Mission assignée :

```json
{
  "type": "mission:assigned",
  "mission_id": 12,
  "mission": {
    "id": 12,
    "status": "ASSIGNED",
    "expected_qr": "a"
  }
}
```

## Robot → serveur

Heartbeat :

```json
{
  "type": "robot.heartbeat",
  "robot_id": "raa-robot-01",
  "mission_id": 12
}
```

Position :

```json
{
  "type": "robot:position",
  "robot_id": "raa-robot-01",
  "mission_id": 12,
  "x": 160,
  "y": 150
}
```

Statut mission :

```json
{
  "type": "mission:updated",
  "robot_id": "raa-robot-01",
  "mission_id": 12,
  "status": "SCANNING_QR"
}
```

Fin de mission :

```json
{
  "type": "mission:completed",
  "robot_id": "raa-robot-01",
  "mission_id": 12
}
```

## États mission

```text
CREATED
ASSIGNED
NAVIGATING_TO_PICKUP
SCANNING_QR
PICKING_UP
NAVIGATING_TO_DROP
DROPPING_OFF
COMPLETED
ERROR
```

Le serveur accepte uniquement la transition normale suivante, ou un passage à `ERROR` depuis un état non terminal. Il refuse les sauts d’étape, les retours arrière et les transitions depuis un état terminal.

## Sécurité

- `robot:emergency_stop` passe la mission active en `ERROR`.
- Un watchdog heartbeat diffuse `robot.timeout` si un robot ne donne plus signe de vie.
- Les positions et statuts sont persistés dans `robot_logs`.
