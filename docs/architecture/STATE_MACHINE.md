# Machine à états des missions

## Rôle du document

Ce document constitue la référence fonctionnelle pour les statuts de mission. Le frontend, l’API REST, le serveur WebSocket, le robot ROS 2, les tests et les diagrammes UML doivent utiliser exactement les mêmes valeurs et les mêmes transitions.

## États autorisés

| État | Signification |
| --- | --- |
| `CREATED` | Mission créée dans l’API, pas encore affectée au robot |
| `ASSIGNED` | Mission affectée à un robot |
| `NAVIGATING_TO_PICKUP` | Navigation vers le point de prise |
| `SCANNING_QR` | Lecture et validation du QR attendu |
| `PICKING_UP` | Prise de l’objet par le bras |
| `NAVIGATING_TO_DROP` | Navigation vers le point de dépôt |
| `DROPPING_OFF` | Dépose de l’objet |
| `COMPLETED` | Mission terminée avec succès |
| `ERROR` | Mission interrompue à la suite d’une erreur ou d’un arrêt de sécurité |

## Transitions autorisées

| État courant | État suivant autorisé |
| --- | --- |
| `CREATED` | `ASSIGNED` ou `ERROR` |
| `ASSIGNED` | `NAVIGATING_TO_PICKUP` ou `ERROR` |
| `NAVIGATING_TO_PICKUP` | `SCANNING_QR` ou `ERROR` |
| `SCANNING_QR` | `PICKING_UP` ou `ERROR` |
| `PICKING_UP` | `NAVIGATING_TO_DROP` ou `ERROR` |
| `NAVIGATING_TO_DROP` | `DROPPING_OFF` ou `ERROR` |
| `DROPPING_OFF` | `COMPLETED` ou `ERROR` |
| `COMPLETED` | aucune transition |
| `ERROR` | aucune transition |

## Règles

1. `COMPLETED` et `ERROR` sont des états terminaux.
2. Une mission terminée ne peut pas reprendre sans création d’une nouvelle mission.
3. Les transitions normales suivent l’ordre défini dans le tableau.
4. `ERROR` peut être atteint depuis tout état non terminal.
5. Un arrêt d’urgence ou un timeout de heartbeat est un événement de sécurité, pas un statut distinct. Il entraîne le passage de la mission à `ERROR` et renseigne `error_reason`.
6. Aucun statut supplémentaire ne doit être introduit sans mise à jour coordonnée de tous les composants et des tests.
7. Toute transition invalide doit être rejetée par le serveur.

## Correspondance avec les événements

| Événement | Effet sur la mission |
| --- | --- |
| `mission:assign` | `CREATED` vers `ASSIGNED` |
| `mission:updated` | transition vers le prochain état normal annoncé par le robot |
| `mission:completed` | `DROPPING_OFF` vers `COMPLETED` |
| `robot:emergency_stop` | état non terminal vers `ERROR` |
| `robot.timeout` | état non terminal vers `ERROR` |

## Sources dans le code

- API REST : `apps/server/src/MissionController.php`
- Serveur WebSocket : `apps/server/realtime/ws_server.py`
- Schéma MySQL : `apps/server/database/schema.sql`
- Robot ROS 2 : `apps/robot/src/m3pro_teacher_vision/m3pro_teacher_vision/mission_executor_node.py`
- Types frontend : `frontend/src/types/mission.ts`
- Types partagés : `packages/shared/mission.ts`
- Tests : `tests/integration/test_missions.py` et `tests/integration/test_websocket.py`
