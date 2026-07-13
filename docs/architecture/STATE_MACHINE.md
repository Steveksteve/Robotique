# Machine à états des missions

Cette page est la référence commune au frontend, à l’API, au serveur WebSocket, au robot et aux tests.

## États

| État | Rôle |
| --- | --- |
| `CREATED` | Mission créée, pas encore affectée |
| `ASSIGNED` | Mission envoyée à un robot |
| `NAVIGATING_TO_PICKUP` | Déplacement vers le point de prise |
| `SCANNING_QR` | Lecture du QR attendu |
| `PICKING_UP` | Prise de l’objet |
| `NAVIGATING_TO_DROP` | Déplacement vers le point de dépôt |
| `DROPPING_OFF` | Dépose de l’objet |
| `COMPLETED` | Mission terminée |
| `ERROR` | Mission arrêtée à la suite d’une erreur ou d’un arrêt de sécurité |

## Transitions acceptées

| État courant | État suivant |
| --- | --- |
| `CREATED` | `ASSIGNED` ou `ERROR` |
| `ASSIGNED` | `NAVIGATING_TO_PICKUP` ou `ERROR` |
| `NAVIGATING_TO_PICKUP` | `SCANNING_QR` ou `ERROR` |
| `SCANNING_QR` | `PICKING_UP` ou `ERROR` |
| `PICKING_UP` | `NAVIGATING_TO_DROP` ou `ERROR` |
| `NAVIGATING_TO_DROP` | `DROPPING_OFF` ou `ERROR` |
| `DROPPING_OFF` | `COMPLETED` ou `ERROR` |
| `COMPLETED` | aucune |
| `ERROR` | aucune |

## Règles appliquées

1. `COMPLETED` et `ERROR` sont terminaux.
2. Les étapes normales doivent être suivies dans l’ordre.
3. Un état non terminal peut passer directement à `ERROR`.
4. Un arrêt d’urgence et un timeout de heartbeat ne sont pas des statuts supplémentaires : ils font passer la mission à `ERROR` et renseignent `error_reason`.
5. L’API et le serveur WebSocket refusent les sauts d’étape et les retours arrière.
6. Toute modification de cette liste doit être reportée dans les composants et les tests.

## Emplacements dans le code

- API : `apps/server/src/MissionController.php`
- WebSocket : `apps/server/realtime/ws_server.py`
- Base de données : `apps/server/database/schema.sql`
- Robot : `apps/robot/src/m3pro_teacher_vision/m3pro_teacher_vision/mission_executor_node.py`
- Frontend : `frontend/src/types/mission.ts`
- Types partagés : `packages/shared/mission.ts`
- Tests : `tests/integration/test_missions.py` et `tests/integration/test_websocket.py`
