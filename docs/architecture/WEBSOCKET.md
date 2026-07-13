# Protocole WebSocket

Le serveur temps réel écoute localement sur `ws://localhost:8765`. Depuis le frontend servi par Nginx, la connexion passe par `/ws`.

Les exemples ci-dessous correspondent aux messages réellement utilisés par le MVP.

## Identification

Dashboard :

```json
{"type":"identify","client_type":"dashboard"}
```

Robot :

```json
{"type":"identify","client_type":"robot","robot_id":"raa-robot-01"}
```

Le serveur confirme l’identification avec :

```json
{"type":"server.ack","message":"identified"}
```

## Affectation d’une mission

Dashboard vers serveur :

```json
{
  "type": "mission:assign",
  "mission_id": 12,
  "robot_id": "raa-robot-01"
}
```

Serveur vers robot :

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

## Messages envoyés par le robot

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

Changement d’état :

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

## Arrêt d’urgence

Dashboard vers serveur :

```json
{
  "type": "robot:emergency_stop",
  "mission_id": 12,
  "reason": "Arrêt demandé depuis le dashboard"
}
```

Le serveur diffuse l’arrêt au robot et passe la mission à `ERROR`.

## Contrôles réalisés par le serveur

- seules les transitions décrites dans [`STATE_MACHINE.md`](STATE_MACHINE.md) sont acceptées ;
- les positions et changements d’état sont enregistrés dans `robot_logs` ;
- un watchdog émet `robot.timeout` si le heartbeat du robot expire ;
- le frontend recharge les missions depuis l’API lors de sa première connexion.

## Limites du MVP

L’identification WebSocket repose actuellement sur un message déclaratif. Il n’y a pas encore d’authentification forte ni de chiffrement WSS dans l’environnement local. Le service ne doit donc pas être exposé tel quel sur Internet.
