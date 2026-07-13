# CI et publication Docker

Les workflows GitHub Actions se trouvent dans `.github/workflows/`.

## Intégration continue

Le workflow `.github/workflows/ci.yml` s’exécute sur les branches `main` et `develop`, lors d’un push, d’une pull request ou d’un lancement manuel.

Il contient quatre contrôles :

1. **PHP** : vérification syntaxique de tous les fichiers PHP du serveur.
2. **Frontend** : installation des dépendances, ESLint et build Vite.
3. **Robot** : compilation syntaxique des sources Python et présence des manifests ROS 2 principaux.
4. **Intégration** : démarrage de MySQL, de l’API, du WebSocket et du frontend avec Docker Compose, puis exécution des tests `pytest`.

Les tests d’intégration couvrent notamment :

- la création et la lecture des missions ;
- le workflow `CREATED` jusqu’à `COMPLETED` ;
- le refus d’une transition invalide ;
- l’écriture des logs ;
- la présence des points de prise et de dépôt ;
- le service du frontend ;
- l’affectation et la progression d’une mission par WebSocket.

Un scan Trivy est aussi exécuté sur l’image de l’API. Il est informatif et ne bloque pas la CI.

## Publication des images

Après une CI réussie, `.github/workflows/cd.yml` construit et publie quatre images dans GitHub Container Registry :

```text
api
realtime
web
robot
```

Chaque image reçoit un tag lié au commit ainsi qu’un tag de canal (`latest` pour `main`, `staging` sinon).

## Déploiement de staging

Le déploiement distant n’a lieu que sur `main` et seulement si les secrets SSH/GHCR ont été configurés. Il déploie la base, l’API, le WebSocket et le frontend, puis vérifie les endpoints de santé.

L’image robot est publiée, mais elle n’est pas lancée sur le serveur de staging : son exécution dépend de la Jetson, des capteurs Yahboom et de ROS 2.

## Ce que la CI ne prouve pas

La CI vérifie le code et le scénario full stack simulé. Elle ne valide pas le déplacement physique, la caméra, le lidar ou le bras du robot réel. Ces essais sont suivis séparément dans [`../robot/ROBOT_FINAL_PIPELINE_STATUS.md`](../robot/ROBOT_FINAL_PIPELINE_STATUS.md).
