# Pipeline CI/CD — Projet Robotique (RAA)

## Objectif

Le projet Robotique/RAA est composé de plusieurs briques :

- une API serveur
- une base de données MySQL
- un client robot
- une interface web

Le pipeline CI/CD a pour rôle de vérifier automatiquement que ces composants peuvent fonctionner ensemble après chaque modification du code.

L’objectif n’est pas seulement de tester la syntaxe, mais de valider un scénario minimal de fonctionnement du système.

## Problème à résoudre

Dans ce projet, le principal risque est qu’un composant fonctionne seul mais ne communique pas correctement avec les autres.

Exemples :
- l’API démarre mais ne se connecte pas à la base
- une mission est envoyée mais n’est pas enregistrée
- le statut d’une mission ne se met pas à jour
- le robot ou l’interface ne récupèrent pas les bonnes données

Le pipeline sert donc à détecter ces erreurs le plus tôt possible.

## Choix techniques

### Docker

Docker permet de lancer chaque service dans un environnement identique.

Avantages :
- évite les différences entre machines
- simplifie le démarrage du projet
- rend les tests reproductibles
- prépare un futur déploiement

### GitHub Actions

GitHub Actions permet d’exécuter automatiquement le pipeline à chaque :
- push
- pull request

Cela garantit que le code est testé avant d’être fusionné.

### Pourquoi Docker Compose / Swarm

Pour ce projet, une orchestration légère suffit.

Le projet reste limité en taille :
- peu de services
- environnement local ou petite infra
- besoin principal : lancer plusieurs briques ensemble

Docker Compose est suffisant pour les tests CI.
Docker Swarm peut être envisagé plus tard pour un déploiement simple multi-services.

### Pourquoi pas Kubernetes

Kubernetes est très puissant mais trop lourd pour le besoin actuel.

Dans notre cas :
- peu de services
- pas de besoin de scalabilité complexe
- projet académique / prototype

L’ajouter maintenant augmenterait surtout la complexité sans bénéfice immédiat.

## Étapes du pipeline

Le pipeline suit les étapes suivantes :

1. Récupérer le code depuis le dépôt GitHub
2. Construire les services nécessaires
3. Démarrer l’environnement de test
4. Vérifier que l’API répond
5. Créer une mission de test
6. Vérifier que la mission est bien enregistrée
7. Vérifier qu’un changement de statut fonctionne
8. Arrêter l’environnement

## Exemple de scénario testé

### Test 1 — disponibilité de l’API
Le pipeline vérifie que l’endpoint principal répond correctement.

### Test 2 — création d’une mission
Le pipeline envoie une mission de test contenant :
- une origine
- une destination
- un objet

Puis il vérifie que cette mission existe bien dans la base de données.

### Test 3 — mise à jour du statut
Le pipeline vérifie qu’une mission peut changer d’état, par exemple :
- CREATED
- ASSIGNED
- COMPLETED

## Conditions de validation

Le pipeline est considéré comme valide si :
- les services démarrent correctement
- l’API répond
- la mission de test est créée
- les données sont bien enregistrées
- les échanges entre composants fonctionnent

Si une de ces étapes échoue, le merge doit être bloqué.

## Bénéfices attendus

Ce pipeline apporte plusieurs avantages :

- détection rapide des erreurs
- validation automatique des interactions entre services
- réduction des bugs d’intégration
- base solide pour un déploiement futur

## Évolution possible

Plus tard, le pipeline pourra être enrichi avec :

- tests plus complets sur les statuts
- tests WebSocket
- tests du client robot
- analyse de qualité du code
- scan de sécurité
- déploiement automatique vers un environnement de démonstration

## Résumé

Le pipeline CI/CD proposé est volontairement simple mais adapté au projet Robotique/RAA.

Il permet de vérifier l’essentiel :
- le démarrage des services
- la communication entre API et base de données
- le bon enregistrement des missions
- la cohérence minimale du système
