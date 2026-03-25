# Pipeline CI/CD - Projet Robotique (RAA)

## Objectif

Le projet Robotique/RAA assemble plusieurs briques :

- une API serveur
- une base MySQL
- un client robot
- une interface web

L'objectif du pipeline est d'automatiser au maximum le chemin entre un commit et un environnement exécutable. Aujourd'hui, le dépôt couvre déjà une vraie chaîne CI et embarque désormais une première chaîne CD pour l'API vers un environnement de staging.

## Ce qui est en place dans le dépôt

### CI

Le workflow [`.github/workflows/ci.yml`](/c:/hetic/Robotique-main/Robotique-main/.github/workflows/ci.yml) se déclenche sur `push` et `pull_request` vers `main` et `develop`.

Il automatise les étapes suivantes :

1. récupération du code
2. démarrage d'un environnement de test Docker via [`docker-compose.test.yml`](/c:/hetic/Robotique-main/Robotique-main/docker-compose.test.yml)
3. attente de disponibilité de l'API
4. exécution des tests d'intégration
5. génération et upload des rapports
6. collecte des logs en cas d'échec
7. nettoyage de l'environnement

Le scénario actuellement validé par les tests d'intégration couvre :

- la disponibilité de l'API
- la création d'une mission
- la lecture des missions
- la mise à jour du statut d'une mission

Les tests concernés sont dans :

- [`tests/integration/test_missions.py`](/c:/hetic/Robotique-main/Robotique-main/tests/integration/test_missions.py)
- [`tests/integration/test_websocket.py`](/c:/hetic/Robotique-main/Robotique-main/tests/integration/test_websocket.py)

### CD

Le workflow [`.github/workflows/cd.yml`](/c:/hetic/Robotique-main/Robotique-main/.github/workflows/cd.yml) ajoute une première chaîne de livraison continue :

1. il attend qu'un run du workflow `CI` se termine avec succès
2. il reconstruit l'image Docker de l'API
3. il pousse cette image dans GitHub Container Registry (`ghcr.io`)
4. sur `main`, il déploie automatiquement l'image sur un serveur de staging via SSH
5. il redémarre les services avec Docker Compose côté serveur et vérifie que l'API répond

Les fichiers de déploiement ajoutés pour cela sont :

- [`deploy/docker-compose.staging.yml`](/c:/hetic/Robotique-main/Robotique-main/deploy/docker-compose.staging.yml)
- [`deploy/.env.staging.example`](/c:/hetic/Robotique-main/Robotique-main/deploy/.env.staging.example)
- [`scripts/deploy_staging.sh`](/c:/hetic/Robotique-main/Robotique-main/scripts/deploy_staging.sh)

## Cible de déploiement actuelle

Le CD cible volontairement uniquement l'API et sa base de données, car ce sont les composants réellement exploitables et testables dans le dépôt à ce stade.

Le déploiement staging repose sur :

- une image API versionnée et poussée sur `ghcr.io`
- un serveur accessible en SSH
- un `docker compose up -d` côté serveur
- une vérification HTTP finale de l'API

## Secrets et variables à configurer dans GitHub

Pour que le déploiement staging fonctionne, il faut définir :

- `STAGING_HOST`
- `STAGING_SSH_PORT`
- `STAGING_SSH_USER`
- `STAGING_SSH_KEY`
- `STAGING_APP_DIR`
- `GHCR_USERNAME`
- `GHCR_TOKEN`

Variable d'environnement GitHub recommandée :

- `API_PORT`

Le serveur doit aussi disposer de Docker et Docker Compose.

## Limites connues

Le pipeline ne couvre pas encore tout le produit de bout en bout :

- `web` n'est pas intégré à la chaîne CD actuelle
- `robot` n'est pas encore déployé automatiquement
- le test WebSocket reste conditionnel tant que `WS_URL` n'est pas fourni
- le staging dépend d'une infrastructure cible et des secrets GitHub associés

En particulier, le dépôt contient un Dockerfile pour `web`, mais le dossier frontend n'a pas encore de build exploitable dans cet état. Il serait donc trompeur de prétendre que le déploiement du front est prêt.

## Lecture honnête de l'avancement

Le projet n'est plus seulement au stade du document :

- la CI est concrète et exécutable
- une première automatisation CD existe pour publier et déployer l'API
- la chaîne "commit -> tests -> image -> staging" est désormais matérialisée dans le dépôt

En revanche, la pipeline CI/CD n'est pas encore complète pour tous les services. La prochaine étape logique est d'intégrer un vrai build web, puis d'étendre le déploiement au front et au client robot si ces composants doivent vivre en environnement partagé.
