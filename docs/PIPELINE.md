# Pipeline CI/CD — Projection

Très bien, on reformule ça de manière plus naturelle et moins “template”.



## Idée générale

Le projet RAA est composé de plusieurs briques techniques qui dépendent les unes des autres : l’API, la base de données, le client robot et l’interface.

Le risque principal n’est pas une erreur de syntaxe isolée, mais un problème de communication entre ces services.

Le pipeline est donc pensé pour vérifier que l’environnement complet démarre correctement et que les échanges entre les différents composants fonctionnent comme prévu.



## Ce que fera le pipeline

1. Construire les images Docker des services.
2. Lancer l’environnement complet (API + DB + robot).
3. Vérifier que l’API répond.
4. Créer une mission de test.
5. Vérifier que la mission est bien enregistrée.
6. Vérifier qu’un changement de statut fonctionne.

Si une étape échoue, on bloque le merge.



## Outils choisis

Docker
Pour éviter les problèmes “ça marche chez moi”.
Chaque service tourne dans son conteneur.

Docker Swarm
Pour gérer les services ensemble :

* réseau interne
* redémarrage automatique
* isolation
* possibilité future d’ajouter un second robot



## Pourquoi pas Kubernetes

Kubernetes est plus adapté à un système distribué à grande échelle.
Notre projet contient peu de services et tourne sur une machine unique.
Mettre Kubernetes maintenant ajouterait surtout de la complexité sans résoudre un problème réel.

Swarm est suffisant pour notre niveau actuel.


## Enchaînement

Push → Build images → Lancer stack → Tester API → Valider → Déployer