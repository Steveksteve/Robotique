# Pipeline final CI/CD — RAA

## Objectif

La pipeline finalise l’intégration des trois briques du projet :

- site opérateur React ;
- API REST + MySQL ;
- communication temps réel WebSocket ;
- workspace robot ROS 2 Humble.

Elle matérialise le chemin complet : commit → vérifications → build full stack → tests d’intégration → publication d’images → déploiement staging.

## CI

Workflow : `.github/workflows/ci.yml`.

Déclencheurs : `push`, `pull_request` sur `main` et `develop`, et lancement manuel.

Jobs :

1. `php-syntax`
   - installe PHP CLI ;
   - vérifie tous les fichiers PHP de `apps/server`.

2. `web-build`
   - installe les dépendances du front ;
   - lance ESLint ;
   - produit le build Vite.

3. `robot-static-checks`
   - compile les sources Python ROS 2 ;
   - vérifie la présence des manifests ROS indispensables.

4. `integration-tests`
   - démarre `db`, `api`, `realtime`, `web` avec `docker-compose.test.yml` ;
   - attend l’API et le front ;
   - exécute les tests pytest ;
   - publie les rapports ;
   - collecte les logs Docker en cas d’échec ;
   - lance un scan Trivy en warning-only.

## Scénarios validés

Les tests d’intégration couvrent :

- création et lecture d’une mission ;
- workflow complet `CREATED → COMPLETED` ;
- rejet d’une transition invalide ;
- logs robot persistants ;
- points `pickup_default` et `dropoff_default` ;
- page web servie par Nginx ;
- affectation mission via WebSocket ;
- progression robot via WebSocket jusqu’à `COMPLETED`.

## CD

Workflow : `.github/workflows/cd.yml`.

Déclencheurs :

- succès de la CI ;
- lancement manuel.

Images publiées dans GitHub Container Registry :

```text
ghcr.io/<owner>/<repo>/api:<sha>
ghcr.io/<owner>/<repo>/realtime:<sha>
ghcr.io/<owner>/<repo>/web:<sha>
ghcr.io/<owner>/<repo>/robot:<sha>
```

Tag canal :

- `latest` pour `main` ;
- `staging` pour les autres branches déclenchées.

## Déploiement staging

Sur `main`, si les secrets sont présents, le job `deploy-staging` :

1. copie `docker-compose.staging.yml`, `.env.staging.example`, `schema.sql` et `deploy_staging.sh` sur le serveur ;
2. se connecte à GHCR ;
3. tire les images immuables ;
4. redémarre `db`, `api`, `realtime`, `web` ;
5. vérifie `/health` côté API et `/` côté web.

## Secrets requis

Minimum pour le déploiement :

- `STAGING_HOST`
- `STAGING_SSH_USER`
- `STAGING_SSH_KEY`
- `GHCR_TOKEN`

Optionnels :

- `STAGING_SSH_PORT` défaut `22`
- `STAGING_APP_DIR` défaut `/opt/robotique`
- `GHCR_USERNAME` défaut `github.actor`
- variables GitHub `API_PORT`, `WEB_PORT`

## Limite assumée

Le robot est buildé et publié en image Docker, mais il n’est pas lancé sur le serveur staging cloud : il doit être lancé sur la Jetson / le robot réel, car il dépend du hardware Yahboom, des capteurs et du réseau ROS 2.
