# Backlog — Robot d’Assistance Autonome (RAA)

# P0 — MVP (Sprints 0 à 2)

Objectif : contrôler le robot avec une manette de PlayStation 3 pour prendre un objet au point A et l’amener au point B.

| Tâche                           | Priorité | Owner | DoD (Definition of Done)        | Dépendances | Estimation |
| ------------------------------- | -------- | ----- | ------------------------------- | ----------- | ---------- |
| Connexion manette PS3 → robot   | P0       | IoT   | Robot contrôlé via manette      | —           | M          |
| Mapping contrôles (déplacement) | P0       | IoT   | Joysticks contrôlent mouvements | Connexion   | M          |
| Commande pince via manette      | P0       | IoT   | Boutons ouvrent/ferment pince   | Connexion   | M          |
| Prise en main objet au point A  | P0       | IoT   | Objet saisi sans chute          | Pince       | M          |
| Déplacement manuel A → B        | P0       | IoT   | Robot atteint point B contrôlé  | Mapping     | M          |
| Dépose objet au point B         | P0       | IoT   | Objet déposé correctement       | Déplacement | M          |
| Test mission complète manuelle  | P0       | Tous  | A→B réussi avec objet           | Toutes P0   | M          |

---

## P1 — Autonomie & Fonctionnalités avancées (Sprints 3 à 7)

Objectif : transformer le robot manuel en robot autonome.

| Tâche                                   | Priorité | Owner    | DoD (Definition of Done)                             | Dépendances         | Estimation |
| --------------------------------------- | -------- | -------- | ---------------------------------------------------- | ------------------- | ---------- |
| Setup repo + environnements             | P1       | Tous     | Projet prêt à coder                                  | —                   | S          |
| Architecture missions + workflow        | P1       | Backend  | États CREATED/NAVIGATING/COMPLETED/ERROR implémentés | Setup               | M          |
| API missions + DB                       | P1       | Backend  | CRUD missions + gestion des états                    | Architecture        | M          |
| Client robot ↔ API                      | P1       | IoT      | Robot reçoit mission et renvoie état                 | API                 | M          |
| Navigation autonome A→B                 | P1       | IoT      | Robot atteint destination seul                       | Client robot        | L          |
| Arrêt sécurité situation anormale       | P1       | IoT      | Robot s’arrête si erreur détectée                    | Navigation          | M          |
| Évitement obstacle simple               | P1       | IoT      | Robot contourne obstacle                             | Navigation          | L          |
| Contrôle pince (ouvrir/fermer) autonome | P1       | IoT      | Commandes fonctionnelles                             | —                   | M          |
| Saisie objet léger autonome             | P1       | IoT      | Objet saisi sans chute                               | Pince               | M          |
| Transport objet A→B autonome            | P1       | IoT      | Objet déplacé avec robot                             | Saisie + Navigation | L          |
| Dépose objet emplacement cible          | P1       | IoT      | Objet déposé correctement                            | Transport           | M          |
| UI déclenchement mission                | P1       | Frontend | Bouton lancer mission OK                             | API missions        | M          |
| Dashboard état mission                  | P1       | Frontend | États affichés                                       | Client robot        | M          |
| Synchronisation état réel ↔ interface   | P1       | Backend  | Interface reflète robot en temps réel                | API/WebSocket       | M          |
| Gestion erreurs + logs                  | P1       | Backend  | Logs exploitables                                    | API                 | M          |
| Reconnexion robot                       | P1       | IoT      | Mission reprend après perte                          | Client robot        | M          |
| Détection situations anormales avancées | P1       | IoT      | Passage automatique état ERROR                       | Navigation          | M          |
| File d’attente missions                 | P1       | Backend  | Queue fonctionnelle                                  | API                 | L          |
| Tests mission complète autonome         | P1       | Tous     | Runs stables                                         | Toutes P1           | L          |
| Optimisation vitesse mission            | P1       | IoT      | Mission plus fluide                                  | Tests               | M          |

---

# P2 — Préparation jury (Sprint final)

Objectif : sécuriser la soutenance.

| Tâche                       | Priorité | Owner   | DoD                    | Dépendances    | Estimation |
| --------------------------- | -------- | ------- | ---------------------- | -------------- | ---------- |
| Répétitions démo            | P2       | Tous    | 10 runs réussis        | Version stable | L          |
| Scénario secours manuel     | P2       | Tous    | Procédure écrite       | Répétitions    | S          |
| Vidéo backup                | P2       | Tous    | Vidéo prête            | Répétitions    | S          |
| Code freeze                 | P2       | CTO     | Version finale figée   | Toutes         | S          |

---

# Légende

S = Small (3–4 jours)
M = Medium (4–6 jours)
L = Large (7–8 jours)
