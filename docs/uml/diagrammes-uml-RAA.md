# Diagrammes UML — RAA

## Diagramme de cas d’utilisation

```mermaid
flowchart LR
    Operateur(["Opérateur"])
    Robot(["Robot autonome"])

    subgraph RAA ["Système RAA"]
        direction TB
        UC1["Créer une mission"]
        UC2["Affecter une mission au robot"]
        UC3["Suivre la mission en temps réel"]
        UC4["Consulter les missions et les logs"]
        UC5["Demander un arrêt d’urgence"]
        UC6["Naviguer vers le point de prise"]
        UC7["Lire et valider le QR"]
        UC8["Prendre l’objet"]
        UC9["Naviguer vers le point de dépôt"]
        UC10["Déposer l’objet"]
        UC11["Signaler une erreur"]
    end

    Operateur --> UC1
    Operateur --> UC2
    Operateur --> UC3
    Operateur --> UC4
    Operateur --> UC5

    Robot --> UC6
    Robot --> UC7
    Robot --> UC8
    Robot --> UC9
    Robot --> UC10
    Robot --> UC11
```

L’arrêt d’urgence est un événement de sécurité. Il place la mission dans l’état persistant `ERROR` et ne crée pas de statut terminal supplémentaire.

## Diagramme d’états — Mission

```mermaid
stateDiagram-v2
    [*] --> CREATED : POST /missions

    CREATED --> ASSIGNED : affectation au robot
    ASSIGNED --> NAVIGATING_TO_PICKUP : démarrage Nav2 vers A
    NAVIGATING_TO_PICKUP --> SCANNING_QR : arrivée au point A
    SCANNING_QR --> PICKING_UP : QR validé
    PICKING_UP --> NAVIGATING_TO_DROP : objet saisi
    NAVIGATING_TO_DROP --> DROPPING_OFF : arrivée au point B
    DROPPING_OFF --> COMPLETED : objet déposé

    CREATED --> ERROR : erreur ou arrêt de sécurité
    ASSIGNED --> ERROR : erreur ou arrêt de sécurité
    NAVIGATING_TO_PICKUP --> ERROR : erreur ou arrêt de sécurité
    SCANNING_QR --> ERROR : erreur ou arrêt de sécurité
    PICKING_UP --> ERROR : erreur ou arrêt de sécurité
    NAVIGATING_TO_DROP --> ERROR : erreur ou arrêt de sécurité
    DROPPING_OFF --> ERROR : erreur ou arrêt de sécurité

    COMPLETED --> [*]
    ERROR --> [*]
```

## Diagramme de séquence — Mission complète

```mermaid
sequenceDiagram
    actor Operateur
    participant Front as Frontend React
    participant WS as Serveur WebSocket
    participant API as API REST
    participant DB as MySQL
    participant Robot as Robot ROS 2

    Operateur ->> Front : Saisit origine, destination, objet et QR
    Front ->> API : POST /missions
    API ->> DB : INSERT status = CREATED
    API -->> Front : Mission créée

    Front ->> WS : mission:assign
    WS ->> DB : UPDATE status = ASSIGNED
    WS -->> Robot : mission:assigned
    WS -->> Front : mission:assigned

    Robot ->> WS : mission:updated NAVIGATING_TO_PICKUP
    WS ->> DB : UPDATE status
    WS -->> Front : mission:updated

    Robot ->> Robot : Navigation Nav2 vers le point A
    Robot ->> WS : robot:position
    WS -->> Front : robot:position

    Robot ->> WS : mission:updated SCANNING_QR
    WS ->> DB : UPDATE status
    Robot ->> Robot : Lecture et validation du QR

    Robot ->> WS : mission:updated PICKING_UP
    WS ->> DB : UPDATE status
    Robot ->> Robot : Séquence de prise du bras

    Robot ->> WS : mission:updated NAVIGATING_TO_DROP
    WS ->> DB : UPDATE status
    Robot ->> Robot : Navigation Nav2 vers le point B

    Robot ->> WS : mission:updated DROPPING_OFF
    WS ->> DB : UPDATE status
    Robot ->> Robot : Séquence de dépose

    Robot ->> WS : mission:completed COMPLETED
    WS ->> DB : UPDATE status = COMPLETED
    WS -->> Front : mission:completed
    Front -->> Operateur : Mission terminée
```

## Diagramme de séquence — Erreur ou arrêt de sécurité

```mermaid
sequenceDiagram
    actor Operateur
    participant Front as Frontend React
    participant WS as Serveur WebSocket
    participant DB as MySQL
    participant Robot as Robot ROS 2

    alt erreur détectée par le robot
        Robot ->> WS : mission:updated status = ERROR
    else arrêt demandé depuis le dashboard
        Operateur ->> Front : Clique sur Stop
        Front ->> WS : robot:emergency_stop
        WS -->> Robot : robot:emergency_stop
    else heartbeat expiré
        WS ->> WS : Détection du timeout
    end

    WS ->> DB : UPDATE status = ERROR et error_reason
    WS ->> DB : INSERT robot_log
    WS -->> Front : mission:updated / robot:emergency_stop / robot.timeout
    Front -->> Operateur : Mission interrompue avec motif
```
