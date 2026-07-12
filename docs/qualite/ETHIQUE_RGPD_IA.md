# Éthique, RGPD et usage de l’intelligence artificielle

## Objet

Cette page décrit les règles retenues pour le MVP RAA concernant les données enregistrées, leur conservation, la sécurité du système et l’usage d’outils d’intelligence artificielle dans la réalisation des livrables.

Le projet est un démonstrateur pédagogique. Il n’est pas conçu pour gérer des dossiers utilisateurs, des comptes clients ou des données sensibles.

## Données traitées

Le système enregistre uniquement les informations techniques nécessaires à l’exécution et au suivi d’une mission :

- identifiant de mission ;
- identifiant technique du robot ;
- libellés génériques d’origine, de destination et d’objet ;
- valeur du QR attendu ;
- coordonnées et orientation des points de prise et de dépôt ;
- coordonnées techniques du robot ;
- statut de la mission ;
- motif d’erreur éventuel ;
- horodatages.

Les logs ne contiennent pas de nom, prénom, adresse électronique, numéro de téléphone, identifiant scolaire, donnée biométrique ou donnée de santé.

Les champs texte doivent rester génériques. Il ne faut pas y saisir le nom d’une personne, une adresse privée ou toute autre information permettant d’identifier directement ou indirectement un individu.

Le flux caméra sert à la navigation, à la détection d’obstacles et à la lecture du QR. Le pipeline final ne sauvegarde pas les images dans la base de données. Aucune reconnaissance faciale n’est utilisée.

## Finalité et minimisation

Les données sont utilisées pour :

- exécuter la mission demandée ;
- afficher sa progression en temps réel ;
- diagnostiquer une erreur technique ;
- démontrer le fonctionnement du système pendant les tests et la soutenance.

Seules les informations utiles à ces finalités sont conservées. Les logs ne doivent pas être enrichis avec des données personnelles ou des contenus sans rapport avec le fonctionnement du robot.

## Durée de conservation

Pour l’environnement pédagogique et de démonstration :

- les logs robot sont conservés au maximum 30 jours ;
- les missions terminées ou en erreur sont conservées au maximum 30 jours après leur dernière mise à jour ;
- les données de test peuvent être supprimées plus tôt après une répétition ou une soutenance ;
- les sauvegardes temporaires doivent suivre la même durée maximale.

La purge peut être exécutée avec le script SQL [`scripts/purge_old_data.sql`](../../scripts/purge_old_data.sql). Dans le MVP actuel, cette purge est une opération d’administration et n’est pas planifiée automatiquement.

## Mesures de sécurité

Les mesures déjà présentes dans le projet comprennent :

- requêtes SQL préparées côté API ;
- validation des statuts et rejet des transitions invalides ;
- séparation des services web, API, base de données et WebSocket ;
- variables d’environnement pour la configuration de déploiement ;
- absence de secret réel dans les fichiers d’exemple ;
- limitation des informations écrites dans les logs ;
- état terminal `ERROR` en cas d’arrêt d’urgence ou de perte de heartbeat ;
- tests de syntaxe, de build, de lint et d’intégration dans la CI.

Pour un déploiement au-delà d’une démonstration locale, les mesures suivantes sont requises :

- authentification des opérateurs ;
- gestion des rôles et des droits ;
- chiffrement HTTPS et WSS ;
- mots de passe de base de données robustes et stockés dans un gestionnaire de secrets ;
- restriction réseau des ports MySQL et WebSocket ;
- journalisation des accès d’administration ;
- sauvegardes chiffrées et procédure de restauration ;
- automatisation de la purge.

Le MVP ne doit pas être exposé directement sur Internet avec les identifiants de développement fournis dans les fichiers Compose.

## Gestion d’un incident de données

Si une donnée personnelle est saisie par erreur :

1. arrêter sa diffusion dans les logs ou les captures de démonstration ;
2. supprimer la valeur concernée de la base et des sauvegardes temporaires ;
3. identifier l’origine de la saisie ;
4. corriger le formulaire, la consigne ou la journalisation afin d’éviter une récidive ;
5. informer l’encadrant si l’incident concerne un rendu pédagogique.

## Usage de l’intelligence artificielle

Des outils d’intelligence artificielle ont pu être utilisés comme appui méthodologique pour :

- structurer ou reformuler une partie de la documentation ;
- proposer des pistes de débogage ;
- relire du code ou des diagrammes ;
- vérifier la cohérence entre plusieurs composants ;
- préparer des scénarios de test.

Les décisions d’architecture, l’intégration, les tests, les corrections et la validation finale restent sous la responsabilité de l’équipe. Une proposition générée par un outil d’IA n’est pas considérée comme correcte tant qu’elle n’a pas été comprise, vérifiée et testée.

Aucune donnée personnelle, aucun mot de passe, aucune clé privée et aucun secret de déploiement ne doit être transmis à un outil d’IA.

## Règles académiques HETIC

Le règlement intérieur HETIC 2025-2026 autorise l’utilisation d’outils d’intelligence artificielle comme appui méthodologique, dans les limites fixées par l’enseignant ou par le cadre de l’évaluation. Une utilisation non autorisée, notamment pendant un examen, un devoir individuel ou un rendu noté, peut être assimilée à de la fraude ou du plagiat.

L’équipe doit donc :

- respecter les consignes propres à chaque matière ;
- signaler l’usage de l’IA lorsqu’une déclaration est demandée ;
- ne pas présenter comme personnel un contenu qui n’a pas été compris ou retravaillé ;
- conserver les preuves de tests et de décisions techniques ;
- être capable d’expliquer chaque partie du rendu pendant la soutenance.

## Déclaration synthétique pour le rendu

> Des outils d’intelligence artificielle ont été utilisés comme appui méthodologique pour la reformulation de la documentation, la revue de cohérence et le diagnostic de certaines erreurs. Tous les choix techniques, modifications, tests et validations ont été réalisés et vérifiés par l’équipe. Aucune donnée personnelle ni aucun secret de déploiement n’a été transmis à ces outils.
