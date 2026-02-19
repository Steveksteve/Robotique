# Backlog

# P0 — MVP (Sprints 0 à 4)

| Tâche | Priorité | Owner | DoD (Definition of Done) | Dépendances | Estimation |
|------|----------|-------|---------------------------|-------------|------------|
Setup repo + environnements | P0 | Tous | Projet prêt à coder | — | S
API missions + DB | P0 | Backend | CRUD missions OK | Setup repo | M
Navigation robot A→B | P0 | IoT | Robot atteint destination | Cartographie | L
Client robot ↔ API | P0 | IoT | Mission reçue et exécutée | API missions | M
UI création mission | P0 | Frontend | Formulaire relié API | API missions | M
Dashboard statut | P0 | Frontend | Statut affiché | Client robot | M
WebSocket temps réel | P0 | Backend | Statuts live | API missions | M
Pick & Drop objet | P0 | IoT | Objet transporté A→B | Navigation | L


---

##  P1 — Robustesse & UX (Sprints 5 à 7)

| Tâche | Priorité | Owner | DoD | Dépendances | Estimation |
|------|----------|-------|-----|-------------|------------|
Évitement obstacles | P1 | IoT | Robot évite obstacle | Navigation | L
Gestion erreurs + logs | P1 | Backend | Erreurs propres | API missions | M
Reconnexion robot | P1 | IoT | Mission reprend | WebSocket | M
File d’attente missions | P1 | Backend | Queue fonctionnelle | API missions | L
Tests & optimisation | P1 | Tous | Version stable | Toutes P0 | L

---

##  P2 — Préparation jury (Sprint 8)

| Tâche | Priorité | Owner | DoD | Dépendances | Estimation |
|------|----------|-------|-----|-------------|------------|
Répétitions démo | P2 | Tous | 10 runs OK | Version stable | L
Scénario secours | P2 | Tous | Procédure prête | Répétitions | S
Vidéo backup | P2 | Tous | Vidéo disponible | Répétitions | S
Code freeze | P2 | CTO | Version finale figée | Toutes | S

---

## Légende

S = Small (3–4 jours)  
M = Medium (4–6 jours)  
L = Large (7–8 jours)
