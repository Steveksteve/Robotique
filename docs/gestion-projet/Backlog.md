# Backlog du projet RAA

Légende : ✅ terminé · 🟡 partiel ou à revalider · ❌ non réalisé.

Les estimations `S`, `M` et `L` sont relatives au projet, pas des durées contractuelles.

## Socle full stack

| Tâche | Pôle | Priorité | État | Critère de validation | Taille |
| --- | --- | --- | --- | --- | --- |
| Structurer le monorepo | Tous | P0 | ✅ | Front, serveur, robot, tests et docs séparés | S |
| Créer l’API des missions | Backend | P0 | ✅ | Création, lecture, mise à jour du statut et suppression | M |
| Persister missions, logs et points | Backend | P0 | ✅ | Schéma MySQL et endpoints consultables | M |
| Définir la machine à états | Backend/IoT | P0 | ✅ | Transitions identiques dans le code et les tests | M |
| Créer le dashboard opérateur | Frontend | P0 | ✅ | Création, affectation, suivi et arrêt d’une mission | M |
| Synchroniser par WebSocket | Backend/Frontend | P0 | ✅ | Missions, positions et heartbeat visibles en direct | L |
| Ajouter le faux robot | IoT | P0 | ✅ | Scénario automatique jusqu’à `COMPLETED` | S |
| Ajouter les tests d’intégration | Tous | P0 | ✅ | Stack Docker testée par `pytest` | M |

## Robot et sécurité

| Tâche | Pôle | Priorité | État | Critère de validation | Taille |
| --- | --- | --- | --- | --- | --- |
| Déployer le workspace sur la Jetson | IoT | P0 | ✅ | Packages construits et détectés par ROS 2 | M |
| Connecter le robot au serveur | IoT/Backend | P0 | ✅ | Identification, heartbeat et réception d’une mission | M |
| Exécuter une mission en `dry_run` | IoT | P0 | ✅ | Tous les statuts sont parcourus depuis le dashboard | M |
| Configurer SLAM et Nav2 | IoT | P0 | ✅ | Navigation réelle entre les zones de la mission | L |
| Lire le QR depuis la caméra | IoT | P0 | ✅ | QR attendu lu pendant la mission réelle | L |
| Commander la prise et la dépose | IoT | P0 | ✅ | Prise et dépose validées après calibrage de la pince | L |
| Gérer l’arrêt d’urgence logiciel | Tous | P0 | ✅ | Mission passée à `ERROR` et ordre diffusé au robot | M |
| Détecter la perte de heartbeat | Backend | P0 | ✅ | Événement `robot.timeout` et mission en `ERROR` | M |
| Reconnecter automatiquement le dashboard | Frontend | P1 | ✅ | Nouvelle tentative après une coupure WebSocket | S |
| Reprendre automatiquement une mission robot | IoT | P1 | ❌ | Reprise contrôlée après coupure réseau | L |
| Ajouter une file de missions | Backend | P2 | ❌ | Plusieurs missions ordonnées et attribuées | L |
| Automatiser le lancement de tous les nœuds | IoT | P1 | 🟡 | Une seule commande de démarrage reste à finaliser | M |
| Externaliser le calibrage de la pince | IoT | P1 | 🟡 | Valeur encore ajustée avant chaque démonstration | S |

## Qualité et rendu

| Tâche | Pôle | Priorité | État | Critère de validation | Taille |
| --- | --- | --- | --- | --- | --- |
| Mettre en place la CI | Tous | P0 | ✅ | PHP, frontend, robot et intégration contrôlés | M |
| Publier les images Docker | DevOps | P1 | ✅ | Images `api`, `realtime`, `web` et `robot` | M |
| Documenter l’état réel des essais | Tous | P0 | ✅ | Réussites et limites séparées clairement | S |
| Préparer une vidéo de secours | Tous | P0 | 🟡 | Utile en cas de temps de redémarrage des nœuds | M |
| Répéter la démonstration réelle | Tous | P0 | ✅ | Mission physique complète reproduite après mise en route | L |
| Ajouter l’authentification et HTTPS/WSS | Backend | P2 | ❌ | Accès protégé hors environnement local | L |
| Automatiser la purge des données | Backend | P2 | ❌ | Tâche planifiée et vérifiée | S |
