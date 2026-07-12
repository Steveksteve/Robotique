# Roadmap — Projet RAA

Présentation jury le 14 juillet. 

---

## Sprint 0 — Setup & cadrage (février)
- Cahier des charges validé
- Diagrammes UML
- Repo Git monorepo + README + CI
- Définition du MVP
- API contract (OpenAPI)
- Setup environnements dev (front, back, robot)

> Livrable : projet structuré, prêt à coder

## Sprint 1 — MVP technique (fin février → début mars)
- API PHP : endpoints création + lecture mission
- Le robot reçoit et accepte une mission
- Navigation basique A → B
- Premier test d'intégration front → back → robot

> Livrable : une mission simple qui s'exécute de bout en bout

## Sprint 2 — Communication temps réel (mars)
- WebSocket entre robot et serveur
- Statut robot affiché en live sur le dashboard
- Position robot mise à jour sur la carte
- Premiers logs robot côté serveur

> Livrable : on voit le robot bouger en temps réel depuis l'interface

## Sprint 3 — Navigation fiable (fin mars → début avril)
- Évitement d'obstacles (Lidar)
- Gestion des erreurs de navigation (robot bloqué, chemin impossible)
- Retry automatique si la mission échoue
- Limitation vitesse pour la sécurité

> Livrable : le robot navigue sans se planter

## Sprint 4 — Manipulation objet (avril)
- Pick-up basique avec le bras
- Drop-off basique
- Vérification que l'objet est bien saisi
- Timeout si le pick échoue

> Livrable : mission complète avec transport d'objet réel

## Sprint 5 — Robustesse système (fin avril → début mai)
- Gestion d'erreurs côté API (retours propres, codes HTTP)
- Reconnexion auto du robot en cas de coupure Wi-Fi
- Heartbeat robot ↔ serveur (détection déconnexion)
- File d'attente si plusieurs missions sont créées

> Livrable : le système tient même quand ça se passe mal

## Sprint 6 — UX + Accessibilité (mai)
- Navigation clavier complète (WCAG AA)
- Notifications de statut (toast, aria-live)
- Bouton arrêt d'urgence toujours visible
- Polish général de l'interface

> Livrable : interface propre et accessible, prête pour la démo

## Sprint 7 — Optimisation + Tests (fin mai → début juin)
- Tests unitaires et d'intégration
- Tests accessibilité (axe-core)
- Optimisation des trajets robot
- Correction des derniers bugs
- Logs détaillés pour le debug

> Livrable : version quasi finale, stable

## Sprint 8 — Préparation jury (juin)
- Minimum 10 répétitions complètes de la démo
- Préparer un scénario B dégradé (si le bras plante, si le Wi-Fi lâche...)
- Filmer une vidéo backup de la démo qui marche
- Stabilisation finale, on ne touche plus au code
- Code freeze fin juin

> Livrable : prototype solide, démo prête pour le 14 juillet
