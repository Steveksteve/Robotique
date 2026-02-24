# Robot d’Assistance Autonome (RAA)

## Vision
Développer une plateforme robotique low-cost (< 500€) destinée à l’optimisation logistique en centre SAV et à l’assistance en environnement professionnel.

---

## Objectifs (MVP)
  **Navigation**
   Autonomie via ROS 2, Nav2 et cartographie Lidar.
  **Manipulation**
   Saisie d’objets à l’aide d’un bras motorisé et d’une cinématique inverse.
  **Interface**
   Dashboard opérateur en React.
  **Sécurité**
   Vitesse maximale de 0.3 m/s et arrêt d’urgence matériel et logiciel.

---

## Architecture (Monorepo)
```
apps/web            → Interface React & TypeScript
apps/server         → API REST, MySQL, WebSockets
apps/robot          → Packages ROS 2 et gestion hardware
packages/shared     → Types et schémas partagés
```

---

## Hardware
  Base : Yahboom Transbot
  Calcul : Jetson Nano
  Capteurs : Lidar et caméra RealSense

---

## Workflow Mission
  CREATED → ASSIGNED → NAVIGATING → INTERACTING → COMPLETED

---

Projet HETIC – Février 2026
