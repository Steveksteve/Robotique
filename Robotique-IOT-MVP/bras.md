# Controle du bras au clavier

Ce document explique le script ajoute pour piloter le bras 6 axes du Yahboom
M3 Pro avec les touches du clavier.

Script cree:

```bash
Robotique/m3pro_teacher_ws/scripts/control_bras_clavier.py
```

Le script publie des messages `arm_msgs/ArmJoints` avec six angles de servo en
degres. Il suit la convention du cours:

- chaque servo va de `0` a `180`;
- `90` est la position centrale;
- la pose de repos sure est `[90, 120, 10, 20, 90, 30]`;
- la pince est ouverte vers `30` et se ferme progressivement vers `75` a `90`.

## Securite

Avant de piloter le vrai bras:

1. Garder les mains, cables et objets fragiles hors de la zone du bras.
2. Tester d'abord en dry-run.
3. Commencer avec un petit pas, par exemple `--step 2`.
4. Ne pas forcer la pince au-dela de ce qui est necessaire.
5. Si le bras part dans le mauvais sens, appuyer sur `q` pour quitter ou `h`
   pour revenir a la pose home.

## Touches clavier

```text
a / d    base gauche / droite
w / s    epaule haut / bas
e / r    coude + / -
i / k    poignet haut / bas
j / l    rotation pince gauche / droite
o / p    pince ouvrir / fermer

h        pose home [90,120,10,20,90,30]
x        pose centre [90,90,90,90,90,30]
+ / -    augmenter / reduire le pas clavier
espace   republier la pose courante
?        afficher l'aide
q        quitter
```

## Lancer en dry-run

Le dry-run affiche les commandes sans bouger le bras.

```bash
cd /root/m3pro_teacher_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
python3 scripts/control_bras_clavier.py --dry-run
```

Depuis ce depot local, si ROS 2 est installe sur la machine:

```bash
cd Robotique/m3pro_teacher_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
python3 scripts/control_bras_clavier.py --dry-run
```

## Lancer sur le robot

Le robot doit deja avoir son bringup et le driver du bras actifs.

Depuis le PC, avec le script existant:

```bash
cd Robotique/m3pro_teacher_ws
ROBOT_HOST=10.10.221.123 CONTAINER=infallible_kare \
  ./scripts/docker_exec_ros.sh \
  python3 scripts/control_bras_clavier.py --topic /arm_control --step 3
```

Si le firmware de votre image Yahboom commande directement `/arm6_joints`,
utiliser:

```bash
ROBOT_HOST=10.10.221.123 CONTAINER=infallible_kare \
  ./scripts/docker_exec_ros.sh \
  python3 scripts/control_bras_clavier.py --topic /arm6_joints --step 3
```

## Lancer depuis un terminal dans le conteneur

```bash
cd /root/m3pro_teacher_ws
source /opt/ros/humble/setup.bash
[ -f /root/yahboomcar_ws/install/setup.bash ] && source /root/yahboomcar_ws/install/setup.bash
[ -f /root/M3Pro_ws/install/setup.bash ] && source /root/M3Pro_ws/install/setup.bash
source install/setup.bash

python3 scripts/control_bras_clavier.py --topic /arm_control --step 3
```

## Options du script

```bash
python3 scripts/control_bras_clavier.py --help
```

Options utiles:

```text
--topic TOPIC          topic de commande du bras, defaut /arm_control
--step N              pas en degres par touche, defaut 5
--servo-time-ms N     duree de mouvement envoyee dans ArmJoints.time, defaut 700
--no-start-publish    ne pas envoyer home au demarrage
--dry-run             afficher sans publier au bras
```

Exemples:

```bash
# Mouvement tres doux
python3 scripts/control_bras_clavier.py --topic /arm_control --step 2 --servo-time-ms 1000

# Test sans mouvement physique
python3 scripts/control_bras_clavier.py --dry-run

# Firmware qui ecoute /arm6_joints
python3 scripts/control_bras_clavier.py --topic /arm6_joints
```

## Verifier les topics

Lister les topics lies au bras:

```bash
ros2 topic list | grep arm
```

Voir l'etat courant publie par le bras:

```bash
ros2 topic echo /arm6_joints
```

Tester une pose home manuellement:

```bash
ros2 topic pub --once /arm_control arm_msgs/msg/ArmJoints \
  "{joint1: 90, joint2: 120, joint3: 10, joint4: 20, joint5: 90, joint6: 30, time: 700}"
```

Si rien ne bouge, essayer le topic direct:

```bash
ros2 topic pub --once /arm6_joints arm_msgs/msg/ArmJoints \
  "{joint1: 90, joint2: 120, joint3: 10, joint4: 20, joint5: 90, joint6: 30, time: 700}"
```

## Principe technique

Le script garde une pose courante en memoire:

```text
[joint1, joint2, joint3, joint4, joint5, joint6]
```

A chaque touche, il modifie un seul servo de `--step` degres, limite la valeur
entre `0` et `180`, puis publie:

```text
arm_msgs/ArmJoints
```

Le champ `time` est rempli si le message `ArmJoints` le possede. Cela permet au
driver Yahboom de lisser le mouvement au lieu de sauter brutalement vers la
nouvelle pose.

## Depannage

Erreur `rclpy est indisponible`:

```bash
source /opt/ros/humble/setup.bash
```

Erreur `No module named arm_msgs` ou dry-run automatique:

```bash
source /root/yahboomcar_ws/install/setup.bash
source /root/M3Pro_ws/install/setup.bash
```

Le bras ne bouge pas:

1. Verifier que le driver Yahboom tourne.
2. Verifier le topic avec `ros2 topic list | grep arm`.
3. Essayer `--topic /arm_control`.
4. Essayer `--topic /arm6_joints`.
5. Tester la commande `ros2 topic pub --once` ci-dessus.

Le clavier ne repond pas:

1. Lancer le script dans un terminal interactif, pas dans un onglet de logs.
2. Verifier que le terminal a le focus.
3. Quitter avec `Ctrl+C` si `q` ne suffit pas.
