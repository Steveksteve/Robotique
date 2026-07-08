# Plan de finalisation 7 jours

## Jour 1 — Merge et installation

- Pousser ce monorepo sur `main` ou branche `develop`.
- Vérifier que GitHub Actions lance la CI.
- Configurer les secrets staging si un serveur est disponible.
- Lancer localement : `./scripts/run_ci_local.sh`.

## Jour 2 — Démo web/API/WebSocket

- Créer une mission depuis le dashboard.
- Lancer `python tests/manual/fake_robot.py`.
- Valider que la mission passe de `CREATED` à `COMPLETED` dans le dashboard.
- Filmer une première vidéo backup de la démo logicielle.

## Jour 3 — Robot dry-run

- Builder l’image robot ou le workspace ROS 2.
- Lancer `mission_mvp.launch.py dry_run:=true simulated_qr:=a`.
- Vérifier la remontée des statuts dans le dashboard avec `ws_url` renseigné.

## Jour 4 — Robot réel navigation

- Lancer bringup Yahboom + SLAM/Nav2.
- Tester uniquement `NAVIGATING_TO_PICKUP` et `NAVIGATING_TO_DROP`.
- Ajuster `pickup_x/y/theta` et `dropoff_x/y/theta` dans la création mission.

## Jour 5 — QR + bras

- Tester le topic caméra compressé.
- Vérifier `/qr/read`.
- Ajuster les poses de bras dans `mission_executor_node.py` si nécessaire.

## Jour 6 — Répétition complète

- Répéter 5 à 10 missions complètes.
- Noter les cas d’échec et préparer un scénario dégradé.
- Filmer une vidéo backup robot réel.

## Jour 7 — Code freeze

- Ne plus ajouter de fonctionnalité.
- Corriger uniquement les bugs bloquants.
- Préparer la présentation : architecture, pipeline, scénario de démo, risques et limites.
