# Roadmap du projet RAA

Cette roadmap retrace le travail réalisé et distingue les fonctions validées des contraintes de mise en route encore manuelles.

Légende : ✅ réalisé · 🟡 partiel · ❌ non réalisé.

## 1. Cadrage et architecture

| Élément | État | Résultat |
| --- | --- | --- |
| Définition du MVP logistique | ✅ | Mission A → QR → prise → B → dépose |
| Organisation du monorepo | ✅ | Frontend, serveur, robot, tests et documentation |
| Diagrammes et machine à états | ✅ | États partagés entre les composants |
| Contrat OpenAPI formel | ❌ | Les routes sont documentées dans le code, sans fichier OpenAPI |

## 2. Application web et API

| Élément | État | Résultat |
| --- | --- | --- |
| CRUD des missions | ✅ | API PHP et persistance MySQL |
| Dashboard opérateur | ✅ | Création, affectation, suivi et arrêt |
| Logs et points cartographiques | ✅ | Endpoints et affichage disponibles |
| Validation des entrées avancée | 🟡 | Champs obligatoires contrôlés, validation encore simple |

## 3. Temps réel

| Élément | État | Résultat |
| --- | --- | --- |
| WebSocket dashboard/robot | ✅ | Affectation, états, positions et heartbeat |
| Reconnexion du dashboard | ✅ | Tentative automatique après coupure |
| Timeout du robot | ✅ | Passage à `ERROR` après expiration du heartbeat |
| Reprise automatique de mission | ❌ | Non implémentée |
| File d’attente de missions | ❌ | Non implémentée |

## 4. Robot ROS 2

| Élément | État | Résultat |
| --- | --- | --- |
| Workspace et packages ROS 2 | ✅ | Build effectué sur le robot |
| Mission en `dry_run` | ✅ | Scénario complet depuis le dashboard |
| SLAM et Nav2 | ✅ | Navigation réelle validée pour la mission |
| Lecture QR réelle | ✅ | QR attendu détecté pendant la mission |
| Pick & place réel | ✅ | Prise et dépose validées après réglage de la pince |
| Mission physique de bout en bout | ✅ | Navigation, QR, prise, transport et dépose jusqu’à `COMPLETED` |
| Démarrage centralisé des nœuds | 🟡 | Les nœuds doivent encore être relancés et contrôlés avant chaque session |
| Calibrage automatique de la pince | 🟡 | La valeur de fermeture est encore adaptée manuellement à l’objet |

## 5. Qualité et préparation du rendu

| Élément | État | Résultat |
| --- | --- | --- |
| CI PHP/frontend/robot | ✅ | Contrôles exécutés par GitHub Actions |
| Tests d’intégration full stack | ✅ | API, web et WebSocket testés avec Docker |
| Publication des images Docker | ✅ | Workflow CD présent |
| Tests d’accessibilité automatisés | ❌ | Aucun test axe-core dans le dépôt |
| Authentification et chiffrement | ❌ | Hors périmètre du MVP local |
| Documentation finale nettoyée | ✅ | Une source principale par sujet |
| Répétitions et vidéo de secours | 🟡 | À confirmer et consigner avant le jury |

## Priorités avant la soutenance

1. figer une valeur de fermeture adaptée à l’objet de démonstration ;
2. préparer une checklist courte pour relancer tous les nœuds dans le bon ordre ;
3. vérifier les topics, les services du bras et la chaîne TF avant le passage ;
4. conserver une vidéo de secours de la mission complète ;
5. répartir les explications entre les membres de l’équipe ;
6. savoir montrer dans le code la contribution de chacun.
