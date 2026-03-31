# Backlog - Robot d'Assistance Autonome (RAA)

# P0 - MVP (Sprints 0 a 2)

Objectif : controler le robot avec une manette de PlayStation 3 pour prendre un objet au point A et l'amener au point B.

| Tache | Priorite | Owner | DoD (Definition of Done) | Dependances | Estimation |
| ----- | -------- | ----- | ------------------------ | ----------- | ---------- |
| Connexion manette PS3 -> robot | P0 | IoT | Robot controle via manette | - | M |
| Mapping controles (deplacement) | P0 | IoT | Joysticks controlent mouvements | Connexion | M |
| Commande pince via manette | P0 | IoT | Boutons ouvrent/ferment pince | Connexion | M |
| Prise en main objet au point A | P0 | IoT | Objet saisi sans chute | Pince | M |
| Deplacement manuel A -> B | P0 | IoT | Robot atteint point B controle | Mapping | M |
| Depose objet au point B | P0 | IoT | Objet depose correctement | Deplacement | M |
| Test mission complete manuelle | P0 | Tous | A->B reussi avec objet | Toutes P0 | M |

---

## P1 - Autonomie et fonctionnalites avancees (Sprints 3 a 7)

Objectif : transformer le robot manuel en robot autonome.

| Tache | Priorite | Owner | DoD (Definition of Done) | Dependances | Estimation |
| ----- | -------- | ----- | ------------------------ | ----------- | ---------- |
| Setup repo + environnements | P1 | Tous | Projet pret a coder | - | S |
| Architecture missions + workflow | P1 | Backend | Etats CREATED/NAVIGATING/COMPLETED/ERROR implementes | Setup | M |
| API missions + DB | P1 | Backend | CRUD missions + gestion des etats | Architecture | M |
| Client robot <-> API | P1 | IoT | Robot recoit mission et renvoie etat | API | M |
| Navigation autonome A->B | P1 | IoT | Robot atteint destination seul | Client robot | L |
| Arret securite situation anormale | P1 | IoT | Robot s'arrete si erreur detectee | Navigation | M |
| Evitement obstacle simple | P1 | IoT | Robot contourne obstacle | Navigation | L |
| Controle pince (ouvrir/fermer) autonome | P1 | IoT | Commandes fonctionnelles | - | M |
| Saisie objet leger autonome | P1 | IoT | Objet saisi sans chute | Pince | M |
| Transport objet A->B autonome | P1 | IoT | Objet deplace avec robot | Saisie + Navigation | L |
| Depose objet emplacement cible | P1 | IoT | Objet depose correctement | Transport | M |
| UI declenchement mission | P1 | Frontend | Bouton lancer mission OK | API missions | M |
| Dashboard etat mission | P1 | Frontend | Etats affiches | Client robot | M |
| Specification messages WebSocket robot -> site | P1 | Backend | Contrat JSON documente pour statuts, position et heartbeat | API missions | S |
| Service WebSocket temps reel | P1 | Backend | Serveur WS accepte robot + dashboard et relaie les evenements | Specification WS | M |
| Robot -> WebSocket | P1 | IoT | Le robot publie statut, position et heartbeat en continu | Service WebSocket | M |
| Site ecoute WebSocket | P1 | Frontend | Le dashboard recoit et affiche les evenements en live | Service WebSocket | M |
| Synchronisation etat reel <-> interface | P1 | Backend | Interface reflete robot en temps reel | API/WebSocket | M |
| Reconnexion et heartbeat WebSocket | P1 | IoT | Reconnexion auto et detection de deconnexion fonctionnent | Robot -> WebSocket | M |
| Test d'integration WebSocket | P1 | Tous | Un test local/CI valide une connexion WS et la reception d'un evenement | Site ecoute WebSocket | M |
| Gestion erreurs + logs | P1 | Backend | Logs exploitables | API | M |
| Reconnexion robot | P1 | IoT | Mission reprend apres perte | Client robot | M |
| Detection situations anormales avancees | P1 | IoT | Passage automatique etat ERROR | Navigation | M |
| File d'attente missions | P1 | Backend | Queue fonctionnelle | API | L |
| Tests mission complete autonome | P1 | Tous | Runs stables | Toutes P1 | L |
| Optimisation vitesse mission | P1 | IoT | Mission plus fluide | Tests | M |

---

# P2 - Preparation jury (Sprint final)

Objectif : securiser la soutenance.

| Tache | Priorite | Owner | DoD | Dependances | Estimation |
| ----- | -------- | ----- | --- | ----------- | ---------- |
| Repetitions demo | P2 | Tous | 10 runs reussis | Version stable | L |
| Scenario secours manuel | P2 | Tous | Procedure ecrite | Repetitions | S |
| Video backup | P2 | Tous | Video prete | Repetitions | S |
| Code freeze | P2 | CTO | Version finale figee | Toutes | S |

---

# Legende

S = Small (3-4 jours)
M = Medium (4-6 jours)
L = Large (7-8 jours)
