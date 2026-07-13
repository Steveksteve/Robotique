# Données, sécurité et usage de l’IA

RAA est un prototype pédagogique. Il ne gère pas de compte client et n’a pas vocation à traiter des données sensibles.

## Données enregistrées

Le système conserve les informations techniques nécessaires à une mission :

- identifiants de mission et de robot ;
- origine, destination et objet sous forme de libellés génériques ;
- QR attendu ;
- coordonnées des points et du robot ;
- statut, motif d’erreur et horodatages.

Aucun nom, courriel, numéro de téléphone, identifiant scolaire, donnée biométrique ou donnée de santé n’est nécessaire au fonctionnement du MVP.

Les champs libres ne doivent pas contenir le nom d’une personne ni une adresse privée. La caméra sert à la navigation et à la lecture du QR ; les images ne sont pas enregistrées dans la base et aucune reconnaissance faciale n’est utilisée.

## Conservation

Pour les essais et la soutenance, l’équipe retient une durée maximale de 30 jours pour les logs et les missions terminées ou en erreur.

Le script [`scripts/purge_old_data.sql`](../../scripts/purge_old_data.sql) permet une purge manuelle. Elle n’est pas automatisée dans la version actuelle.

## Sécurité présente dans le MVP

- requêtes SQL préparées ;
- contrôle des transitions de mission ;
- services séparés par conteneur ;
- configuration par variables d’environnement ;
- arrêt d’urgence et timeout de heartbeat ;
- contrôles de syntaxe, lint, build et intégration dans la CI.

Limites connues :

- pas d’authentification des opérateurs ;
- pas de gestion de rôles ;
- HTTP et WebSocket non chiffrés en local ;
- identifiants de développement dans les fichiers Compose ;
- purge non planifiée automatiquement.

Le MVP ne doit donc pas être exposé directement sur Internet dans cette configuration.

## Usage de l’intelligence artificielle

Des assistants d’IA générative ont été utilisés pendant le projet pour :

- reformuler certains passages de documentation ;
- proposer des pistes de débogage ;
- relire la cohérence de fichiers ou de diagrammes ;
- suggérer des scénarios de test.

Les réponses obtenues ont été relues et adaptées par l’équipe. Les fonctionnalités conservées ont été vérifiées dans le code ou pendant les tests. Une proposition d’IA n’est pas considérée comme validée simplement parce qu’elle est bien formulée.

Aucune donnée personnelle, aucun mot de passe, aucune clé privée et aucun secret de déploiement ne doit être envoyé à un outil d’IA.

L’usage de ces outils doit aussi respecter les consignes propres à chaque enseignant et à chaque évaluation.

## Déclaration courte pour le rendu

> Des assistants d’IA générative ont été utilisés pour la reformulation de certains textes, la recherche de pistes de débogage et la préparation de tests. Les propositions retenues ont été relues, adaptées et vérifiées par l’équipe. Aucun secret de déploiement ni aucune donnée personnelle n’a été transmis à ces outils.
