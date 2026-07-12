# Exercice : SLAM, Navigation autonome et ramassage d'objets avec le bras

Objectif: comprendre et mettre en oeuvre la cartographie SLAM, la navigation
autonome Nav2, le tableau de bord web, la détection d'objets par caméra et
le ramassage avec le bras robotique.

Vous allez:

1. vérifier les prérequis et compiler les nouveaux paquets;
2. comprendre ce qu'est le SLAM et comment il fonctionne;
3. construire une carte de la salle avec slam_toolbox;
4. sauvegarder la carte;
5. lancer la navigation autonome Nav2 sur cette carte;
6. envoyer des objectifs de navigation;
7. lancer le tableau de bord web pour surveiller le robot à distance;
8. comprendre la détection d'objets par couleur HSV;
9. lancer la détection et observer les résultats;
10. comprendre la cinématique inverse du bras;
11. lancer le ramassage automatique;
12. tout intégrer: le robot explore, détecte et ramasse;
13. nettoyer.

Important: le buzzer doit rester désactivé. Le bras ne doit être activé que
lorsque l'enseignant donne l'autorisation.

## Matériel

- Robot Yahboom ROSMASTER M3 Pro allumé.
- Ordinateur connecté au même réseau.
- Accès SSH au robot.
- VNC ou écran sur le Jetson pour voir RViz.
- Objets colorés à poser au sol (balles, cubes).

Dans cet exercice, on utilise:

```text
Robot: jetson@10.10.221.123
ROS2: dans Docker
Workspace démo: /root/m3pro_teacher_ws
```

## Rappel: architecture du robot

```text
            scan0 (lidar avant, 180°)
                  ↓
sensor_fusion_rgb_demo ←── scan1 (lidar arrière, 180°)
                  ↓
    /teacher/scan_merged (360°)
                  ↓
    ┌─────────────┼────────────────┐
    ↓             ↓                ↓
slam_toolbox    Nav2         Détection vision
 (carte)     (planif. +       (OpenCV + depth)
              contrôle)            ↓
    ↓             ↓          Pick & Place
  /map        /cmd_vel        (bras IK)
```

Les topics importants:

```text
/scan0                   → lidar avant (LaserScan)
/scan1                   → lidar arrière (LaserScan)
/teacher/scan_merged     → scan fusionné 360° (LaserScan)
/odom_raw                → odométrie Yahboom brute (Odometry)
/odom                    → odométrie standard créée par odom_raw_bridge
/cmd_vel                 → commande de vitesse (Twist)
/camera/color/image_raw  → image RGB (Image)
/camera/depth/image_raw  → image profondeur (Image)
/map                     → carte construite (OccupancyGrid)
/arm6_joints             → positions actuelles du bras (ArmJoints)
```

---

# Partie A: SLAM — Construire une carte

---

## Partie 1: Préparer l'environnement

Connectez-vous au robot et entrez dans Docker:

```bash
ssh jetson@10.10.221.123
```

Lancez l'agent Jetson du robot:

```bash
bash /home/jetson/start_agent.sh
```

Depuis le PC Ubuntu/WSL, déployez le workspace vers le robot et compilez-le dans Docker:

```bash
ssh jetson@10.10.221.123 'bash /home/jetson/start_agent.sh'

cd /mnt/c/hetic/aaaa/m3pro_teacher_ws
CONTAINER=infallible_kare ./scripts/deploy_workspace_to_robot.sh 10.10.221.123
```

```bash
docker exec -it \
  -e ROS_DOMAIN_ID=30 \
  -e FASTDDS_BUILTIN_TRANSPORTS=UDPv4 \
  -e DISPLAY=:0 \
  infallible_kare \
  bash
```

Sourcez les workspaces:

```bash
source /opt/ros/humble/setup.bash
source /root/yahboomcar_ws/install/setup.bash 2>/dev/null || true
source /root/M3Pro_ws/install/setup.bash 2>/dev/null || true
source /root/m3pro_teacher_ws/install/setup.bash
```

## Partie 2: Installer les dépendances

Vérifiez que les paquets SLAM et Nav2 sont installés:

```bash
ros2 pkg list | grep -E "slam_toolbox|nav2"
```

Si rien n'apparaît, installez-les:

```bash
sudo apt update
sudo apt install -y ros-humble-slam-toolbox
sudo apt install -y ros-humble-navigation2 ros-humble-nav2-bringup
sudo apt install -y ros-humble-rosbridge-server
```

Puis recompilez le workspace:

```bash
cd /root/m3pro_teacher_ws
colcon build --symlink-install
source install/setup.bash
```

Vérifiez que les nouveaux paquets apparaissent:

```bash
ros2 pkg list | grep m3pro_teacher
```

Résultat attendu:

```text
m3pro_teacher_demos
m3pro_teacher_description
m3pro_teacher_nav
m3pro_teacher_vision
m3pro_teacher_web
```

## Partie 3: Comprendre le SLAM

SLAM signifie Simultaneous Localization And Mapping. Cela veut dire que le
robot construit une carte de son environnement tout en se localisant dessus
en même temps.

Pour fonctionner, le SLAM a besoin de deux choses:

```text
1. Un capteur de distance (lidar) → pour voir les murs et obstacles
2. L'odométrie (roues) → pour estimer le déplacement du robot
```

Le processus:

```text
Le robot avance → le lidar mesure les distances →
slam_toolbox compare le nouveau scan avec les précédents →
il met à jour la carte et corrige la position du robot
```

Question:

```text
Pourquoi l'odométrie seule ne suffit pas pour construire une carte ?
```

Réponse:

```text
L'odométrie dérive avec le temps. Les roues glissent, les mesures
s'accumulent et la position estimée s'éloigne de la réalité. Le SLAM
utilise le lidar pour corriger cette dérive.
```

Question:

```text
Pourquoi le lidar seul ne suffit pas non plus ?
```

Réponse:

```text
Le lidar mesure des distances à un instant donné mais ne sait pas
combien le robot a bougé entre deux mesures. Sans odométrie, il ne
peut pas placer les scans les uns par rapport aux autres.
```

## Partie 4: Vérifier les capteurs avant de lancer le SLAM

Vérifiez que le lidar et l'odométrie publient des données:

```bash
ros2 topic hz /scan0
```

Résultat attendu: environ 10 Hz. Arrêtez avec `Ctrl-C`.

```bash
ros2 topic hz /odom_raw
```

Résultat attendu: environ 20-50 Hz. Arrêtez avec `Ctrl-C`.

Le robot publie l'odométrie brute sur `/odom_raw`. Le workspace lance
`odom_raw_bridge`, qui republie `/odom` et la TF `odom → base_link`.

Vérifiez que l'arbre TF est correct:

```bash
ros2 run tf2_ros tf2_echo odom base_link
```

Résultat attendu: vous devez voir une translation et une rotation qui
changent quand le robot bouge.

Question:

```text
Que représente la transformation odom → base_link ?
```

Réponse:

```text
C'est la position estimée du robot par rapport à son point de départ.
L'odométrie calcule cette transformation à partir de la rotation des
roues.
```

## Partie 5: Lancer le SLAM

Ouvrez VNC sur votre ordinateur:

```text
vnc://10.10.221.123:5900
```

Dans un terminal Docker:

```bash
ros2 launch m3pro_teacher_nav slam_online.launch.py
```

Ce que cette commande lance:

```text
1. robot_state_publisher    → publie les transformations URDF
2. arm_joint_state_bridge   → pont pour les articulations du bras
3. sensor_fusion_rgb_demo   → fusionne scan0 + scan1 en un scan 360°
4. slam_toolbox             → algorithme SLAM
5. rviz2                    → visualisation
```

Ce que vous devez voir dans RViz:

- Le robot apparaît au centre.
- Un scan laser vert/cyan apparaît autour du robot.
- Une carte grise commence à se construire.
- La carte a trois couleurs: blanc = libre, noir = obstacle, gris = inconnu.

Question:

```text
Quel topic contient la carte construite par le SLAM ?
```

Réponse:

```text
/map
```

Question:

```text
Quel type de message est la carte ?
```

Réponse:

```text
nav_msgs/msg/OccupancyGrid
```

Vérifiez dans un autre terminal Docker:

```bash
ros2 topic info /map
```

## Partie 6: Construire la carte en conduisant le robot

Ouvrez un nouveau terminal Docker. Sourcez les workspaces puis lancez la
téléopération au clavier:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Les touches:

```text
   u    i    o        ← tourner + avancer
   j    k    l        ← tourner / arrêter / tourner
   m    ,    .        ← tourner + reculer

k = arrêt complet
q/z = augmenter/diminuer la vitesse
```

Conseils pour une bonne carte:

```text
1. Roulez lentement (0.10 à 0.15 m/s maximum)
2. Faites des mouvements réguliers, pas de secousses
3. Longez les murs à environ 50 cm
4. Faites une boucle complète de la salle
5. Repassez par le point de départ → cela permet la fermeture de boucle
```

Observez la carte se construire dans RViz pendant que vous conduisez.

Question:

```text
Que se passe-t-il quand le robot repasse par un endroit déjà cartographié ?
```

Réponse:

```text
slam_toolbox détecte la correspondance avec les scans précédents et
corrige les erreurs accumulées. C'est la fermeture de boucle (loop
closure).
```

## Partie 7: Examiner la configuration du SLAM

Pendant que le SLAM tourne, ouvrez le fichier de configuration:

```bash
sed -n '1,60p' /root/m3pro_teacher_ws/src/m3pro_teacher_nav/config/slam_toolbox_params.yaml
```

Cherchez ces paramètres:

```text
scan_topic: /teacher/scan_merged
base_frame: base_link
odom_frame: odom
map_frame: map
resolution: 0.05
max_laser_range: 3.5
do_loop_closing: true
```

Question:

```text
Que signifie resolution: 0.05 ?
```

Réponse:

```text
Chaque cellule de la carte mesure 5 centimètres. Plus la valeur est
petite, plus la carte est détaillée mais plus elle consomme de mémoire.
```

Question:

```text
Pourquoi utilise-t-on /teacher/scan_merged plutôt que /scan0 seul ?
```

Réponse:

```text
/teacher/scan_merged combine les lidars avant et arrière pour obtenir
un scan à 360 degrés. Cela donne plus d'informations au SLAM et
produit une meilleure carte.
```

Question:

```text
Quels sont les trois repères TF utilisés par le SLAM ?
```

Réponse:

```text
map → odom → base_link

- map est le repère fixe de la carte
- odom est le repère d'odométrie (dérive avec le temps)
- base_link est le repère principal du robot

Le SLAM publie la transformation map → odom pour corriger la dérive.
```

## Partie 8: Sauvegarder la carte

Quand la carte vous semble complète, sauvegardez-la.

Dans un nouveau terminal Docker:

```bash
source /opt/ros/humble/setup.bash
ros2 run nav2_map_server map_saver_cli \
  -f /root/m3pro_teacher_ws/src/m3pro_teacher_nav/maps/salle
```

Résultat attendu:

```text
[INFO] Map saved successfully
```

Vérifiez que deux fichiers ont été créés:

```bash
ls -la /root/m3pro_teacher_ws/src/m3pro_teacher_nav/maps/
```

```text
salle.pgm   → image de la carte (niveaux de gris)
salle.yaml  → métadonnées (résolution, origine, seuils)
```

Pour récupérer la carte sur votre PC:

```bash
ssh jetson@10.10.221.123 \
'docker cp infallible_kare:/root/m3pro_teacher_ws/src/m3pro_teacher_nav/maps /home/jetson/maps'

scp -r jetson@10.10.221.123:/home/jetson/maps ./maps
```

Affichez les métadonnées:

```bash
cat /root/m3pro_teacher_ws/src/m3pro_teacher_nav/maps/salle.yaml
```

Résultat attendu:

```yaml
image: salle.pgm
mode: trinary
resolution: 0.05
origin: [-X.XX, -Y.YY, 0]
negate: 0
occupied_thresh: 0.65
free_thresh: 0.25
```

Question:

```text
Que signifient occupied_thresh et free_thresh ?
```

Réponse:

```text
Ce sont les seuils pour décider si une cellule est occupée ou libre.
Si la probabilité d'occupation est > 0.65, la cellule est un obstacle.
Si elle est < 0.25, la cellule est libre. Entre les deux, c'est
inconnu.
```

Arrêtez le SLAM et la téléopération avec `Ctrl-C` dans les terminaux
correspondants.

## Partie 8b: Exploration autonome (mode Roomba)

Au lieu de conduire manuellement le robot, on peut lui faire explorer la
salle tout seul. Le noeud `frontier_explorer_demo` analyse la carte en
construction pour trouver les frontières (limites entre zones connues et
inconnues) et envoie automatiquement le robot les explorer.

Pour cela, il faut d'abord lancer SLAM + Navigation ensemble:

```bash
ros2 launch m3pro_teacher_nav slam_and_nav.launch.py
```

Puis dans un autre terminal:

```bash
ros2 run m3pro_teacher_demos frontier_explorer_demo
```

Ce que vous devez voir:

```text
[INFO] Frontier explorer started — waiting for map and odometry...
[INFO] Goal #1: frontier at (1.23, 0.45), size=42 cells, 5 frontiers remaining
[INFO] Reached goal, looking for next frontier...
[INFO] Goal #2: frontier at (-0.80, 1.12), size=28 cells, 3 frontiers remaining
...
[INFO] No more frontiers! Map is complete. Sent 12 goals total.
```

Le robot se déplace tout seul de frontière en frontière jusqu'à ce que
toute la salle soit cartographiée.

L'algorithme:

```text
1. Lire la carte (/map) publiée par slam_toolbox
2. Trouver les cellules frontières:
   cellule libre (0) voisine d'une cellule inconnue (-1)
3. Regrouper les frontières proches en clusters
4. Choisir le cluster le plus proche du robot
5. Envoyer un objectif Nav2 vers son centre
6. Attendre l'arrivée, puis recommencer
7. S'arrêter quand il n'y a plus de frontières
```

Question:

```text
Que se passe-t-il si le robot est bloqué et ne peut pas atteindre
une frontière ?
```

Réponse:

```text
Après 20 secondes sans mouvement significatif (stuck_timeout), le
noeud abandonne cette frontière et en choisit une autre.
```

Arrêtez l'exploration avec `Ctrl-C` puis sauvegardez la carte comme
dans la Partie 8.

---

# Partie B: Navigation autonome avec Nav2

---

## Partie 9: Comprendre Nav2

Nav2 est la pile de navigation de ROS2. Elle permet au robot de se déplacer
de manière autonome d'un point A à un point B en évitant les obstacles.

Nav2 est composé de plusieurs éléments:

```text
1. map_server     → charge la carte sauvegardée
2. AMCL           → localise le robot sur la carte (particules)
3. planner_server → calcule le chemin global (A* ou Dijkstra)
4. controller     → suit le chemin en évitant les obstacles locaux
5. behavior_server→ gère les cas bloqués (demi-tour, recul, attente)
6. bt_navigator   → orchestre le tout avec un arbre de comportements
```

Le flux de navigation:

```text
Vous envoyez un objectif (x, y, orientation) sur la carte
     ↓
AMCL localise le robot sur la carte
     ↓
Le planner calcule un chemin global
     ↓
Le controller suit le chemin en temps réel
     ↓
Si le robot est bloqué, le behavior_server intervient
     ↓
Le robot arrive à destination
```

Question:

```text
Quelle est la différence entre le planificateur global et le
contrôleur local ?
```

Réponse:

```text
Le planificateur global calcule le chemin complet sur la carte en
évitant les murs connus. Le contrôleur local ajuste le mouvement en
temps réel pour éviter les obstacles imprévus (une personne qui passe,
un objet déplacé).
```

## Partie 10: Comprendre les costmaps

Nav2 utilise deux costmaps (cartes de coût):

```text
global_costmap → basée sur la carte + obstacles connus
local_costmap  → fenêtre glissante autour du robot avec le lidar live
```

Chaque cellule a un coût:

```text
0         = libre (le robot peut y aller)
1-252     = zone d'inflation (proche d'un obstacle)
253       = possiblement en collision
254       = en collision certaine
255       = inconnu
```

La couche d'inflation ajoute un dégradé autour des obstacles pour que le
robot garde ses distances.

Ouvrez le fichier de configuration Nav2:

```bash
sed -n '100,150p' /root/m3pro_teacher_ws/src/m3pro_teacher_nav/config/nav2_params.yaml
```

Cherchez:

```text
footprint
inflation_radius
cost_scaling_factor
```

Question:

```text
À quoi correspond le footprint du robot ?
```

Réponse:

```text
C'est le contour du robot vu de dessus, en mètres. Nav2 utilise cette
forme pour vérifier si le robot rentre dans un passage. Le M3 Pro
fait environ 0.38m x 0.32m avec marge.
```

## Partie 11: Lancer la navigation avec la carte

Assurez-vous que le bringup Yahboom tourne dans un autre terminal.

Dans un terminal Docker:

```bash
ros2 launch m3pro_teacher_nav navigation.launch.py \
  map:=/root/m3pro_teacher_ws/src/m3pro_teacher_nav/maps/salle.yaml
```

Ce que vous devez voir dans RViz:

- La carte sauvegardée apparaît.
- Le robot apparaît mais peut-être au mauvais endroit.
- Le scan laser doit être visible.
- Les costmaps (colorées) doivent apparaître autour des obstacles.

Si RViz affiche `Frame [map] does not exist`, c'est normal tant qu'AMCL n'a
pas reçu de pose initiale. AMCL publie la transformation `map → odom`
seulement après cette initialisation.

## Partie 12: Localiser le robot sur la carte

Le robot ne sait pas encore où il est sur la carte. Il faut lui donner une
position initiale.

Dans RViz:

```text
1. Cliquez sur "2D Pose Estimate" dans la barre d'outils
2. Cliquez sur la carte à l'endroit où le robot se trouve réellement
3. Maintenez le clic et glissez pour indiquer la direction du robot
4. Relâchez
```

Ce que vous devez voir:

- Un nuage de particules vertes apparaît autour du robot.
- Le scan laser doit s'aligner avec les murs de la carte.
- Les particules convergent après quelques secondes.

Si le scan ne s'aligne pas avec les murs, recommencez l'estimation de pose.

Alternative en ligne de commande si RViz ne publie pas la pose:

```bash
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
"{header: {frame_id: 'map'}, pose: {pose: {position: {x: 0.0, y: 0.0, z: 0.0}, orientation: {w: 1.0}}, covariance: [0.25, 0, 0, 0, 0, 0, 0, 0.25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0685]}}"
```

Vérifiez ensuite les TF:

```bash
ros2 run tf2_ros tf2_echo odom base_link
ros2 run tf2_ros tf2_echo map odom
```

La chaîne attendue est `map → odom → base_link`.

Question:

```text
Comment AMCL localise-t-il le robot ?
```

Réponse:

```text
AMCL utilise un filtre à particules. Chaque particule est une
hypothèse de position. Il compare ce que le lidar mesure avec ce que
la carte prédit. Les particules qui correspondent bien survivent, les
autres disparaissent. Après quelques itérations, les particules
convergent vers la vraie position.
```

Vérifiez la localisation dans un autre terminal:

```bash
ros2 topic echo /amcl_pose --once
```

Résultat attendu: une position (x, y) et une orientation cohérentes avec
la position réelle du robot.

## Partie 13: Envoyer un objectif de navigation

Méthode 1 — avec RViz:

```text
1. Cliquez sur "2D Goal Pose" dans la barre d'outils (ou touche G)
2. Cliquez sur la carte à l'endroit souhaité
3. Glissez pour indiquer l'orientation d'arrivée
4. Relâchez
```

Ce que vous devez voir:

- Un chemin vert/bleu apparaît entre le robot et l'objectif.
- Le robot commence à bouger.
- Le robot évite les obstacles et suit le chemin.
- Le robot s'arrête à l'objectif.

Méthode 2 — en ligne de commande:

```bash
ros2 topic pub --once /goal_pose geometry_msgs/msg/PoseStamped \
  "{header: {frame_id: 'map'}, pose: {position: {x: 1.0, y: 0.5, z: 0.0}, orientation: {w: 1.0}}}"
```

Question:

```text
Que signifie orientation: {w: 1.0} ?
```

Réponse:

```text
C'est un quaternion qui représente une rotation nulle (pas de
rotation). Le robot arrivera orienté vers l'axe X de la carte. Pour
une rotation de 90°, on utiliserait z: 0.707, w: 0.707.
```

## Partie 14: Observer la navigation en détail

Pendant que le robot navigue, observez les topics dans un autre terminal:

```bash
ros2 topic echo /cmd_vel
```

Ce que vous devez voir:

```text
linear:
  x: 0.12    ← vitesse linéaire (m/s)
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: -0.15   ← vitesse de rotation (rad/s)
```

Annulez la navigation si nécessaire:

```bash
ros2 topic pub --once /navigate_to_pose/_action/cancel_goal \
  action_msgs/msg/CancelGoal "{}"
```

Question:

```text
Que publie Nav2 sur /cmd_vel et qui le consomme ?
```

Réponse:

```text
Nav2 publie des commandes de vitesse (Twist). Le driver moteur du
robot (Yahboom bringup) les reçoit et fait tourner les roues en
conséquence.
```

## Partie 15: Examiner la configuration de vitesse

```bash
sed -n '55,95p' /root/m3pro_teacher_ws/src/m3pro_teacher_nav/config/nav2_params.yaml
```

Cherchez:

```text
max_vel_x: 0.20
max_vel_theta: 0.8
xy_goal_tolerance: 0.15
yaw_goal_tolerance: 0.25
```

Question:

```text
Que se passe-t-il si on augmente max_vel_x à 0.5 ?
```

Réponse:

```text
Le robot roulera plus vite mais aura plus de mal à s'arrêter
précisément. Dans un environnement intérieur avec des meubles et des
personnes, 0.20 m/s est une vitesse prudente.
```

Question:

```text
Que signifie xy_goal_tolerance: 0.15 ?
```

Réponse:

```text
Le robot considère qu'il est arrivé quand il est à moins de 15 cm de
l'objectif. Une tolérance plus petite oblige le robot à s'approcher
davantage mais rend l'arrivée plus lente.
```

## Partie 16: SLAM + Navigation en même temps

Il est possible de construire la carte et naviguer en même temps. Le robot
explore l'environnement tout en pouvant recevoir des objectifs de
navigation.

Arrêtez les programmes précédents avec `Ctrl-C`.

Lancez le mode combiné:

```bash
ros2 launch m3pro_teacher_nav slam_and_nav.launch.py
```

Ce que cette commande lance:

```text
- slam_toolbox       → construit la carte en temps réel
- controller_server  → suit les chemins
- planner_server     → planifie les chemins sur la carte en cours
- behavior_server    → gère les situations bloquées
- bt_navigator       → orchestre la navigation
```

Envoyez un objectif dans RViz. Le robot va s'y rendre tout en
cartographiant le chemin.

Question:

```text
Pourquoi n'a-t-on pas besoin d'AMCL dans ce mode ?
```

Réponse:

```text
Parce que slam_toolbox fournit déjà la localisation. C'est lui qui
publie la transformation map → odom. AMCL n'est nécessaire que
lorsqu'on utilise une carte déjà construite.
```

## Partie 16b: Détection visuelle d'obstacles par caméra

Les lidars 2D ne voient que dans un plan horizontal. Ils ratent les petits
objets au sol, les surfaces transparentes et les obstacles en dessous de
leur hauteur de scan. La caméra de profondeur complète le lidar en
regardant vers le bas.

Le noeud `camera_obstacle_node` convertit l'image de profondeur en un
scan laser virtuel que Nav2 utilise dans sa costmap, exactement comme un
vrai lidar.

Lancez la caméra si ce n'est pas déjà fait:

```bash
ros2 launch slam_mapping app_camera.launch.py
```

Puis lancez la détection d'obstacles caméra:

```bash
ros2 run m3pro_teacher_vision camera_obstacle_node
```

Vérifiez le scan virtuel:

```bash
ros2 topic echo /teacher/camera_scan --once
```

Résultat attendu: un message LaserScan similaire aux vrais lidars mais
avec `frame_id: camera_color_optical_frame`.

Observez l'image annotée:

```bash
ros2 run rqt_image_view rqt_image_view /teacher/camera_obs_image
```

Ce que vous devez voir:

- Une ligne jaune horizontale montre la zone de scan dans l'image.
- Les obstacles détectés sont encadrés en rouge avec leur distance.

Le schéma de fonctionnement:

```text
Image de profondeur
       ↓
Bande inférieure de l'image (zone sol)
       ↓
Pour chaque colonne: distance minimale
       ↓
LaserScan virtuel (/teacher/camera_scan)
       ↓
Nav2 costmap (même traitement qu'un vrai lidar)
```

Question:

```text
Pourquoi le scan caméra a-t-il clearing: false dans la costmap
alors que le scan lidar a clearing: true ?
```

Réponse:

```text
Le clearing efface les obstacles quand le rayon passe à travers
sans rien toucher. Le champ de vision de la caméra est plus étroit
que le lidar 360°. Si on activait le clearing sur la caméra, elle
effacerait les obstacles vus par le lidar mais hors de son champ de
vision. On utilise la caméra uniquement pour ajouter des obstacles,
pas pour les effacer.
```

---

# Partie C: Tableau de bord web

---

## Partie 17: Lancer le tableau de bord

Le tableau de bord web permet de surveiller le robot depuis n'importe quel
navigateur sur le réseau. Il n'y a rien à installer côté ordinateur.

Dans un nouveau terminal Docker:

```bash
source /opt/ros/humble/setup.bash
source /root/m3pro_teacher_ws/install/setup.bash

ros2 launch m3pro_teacher_web web_dashboard.launch.py
```

Ce que cette commande lance:

```text
1. rosbridge_websocket → pont WebSocket sur le port 9090
2. web_server_node     → serveur HTTP sur le port 8080
```

## Partie 18: Ouvrir le tableau de bord

Sur votre ordinateur, ouvrez un navigateur et allez à:

```text
http://10.10.221.123:8080
```

Remplacez l'adresse IP par celle de votre robot.

Ce que vous devez voir:

- En haut: le statut de connexion passe à "CONNECTED" (vert).
- Panneau carte: la carte apparaît si le SLAM ou map_server tourne.
- Panneau caméra: l'image de la caméra apparaît si la caméra est lancée.
- Panneau état: position, vitesse, obstacle le plus proche.
- Panneau contrôles: boutons pour envoyer un objectif, annuler, sauvegarder.

## Partie 19: Utiliser le tableau de bord

Pour envoyer un objectif de navigation depuis le navigateur:

```text
1. Cliquez sur la carte à l'endroit souhaité (un point orange apparaît)
2. Cliquez sur le bouton "Send Nav Goal"
3. Le robot se déplace vers cet endroit
```

Pour annuler:

```text
Cliquez sur "Cancel Navigation"
```

Pour sauvegarder la carte:

```text
Cliquez sur "Save Map" (sauvegarde dans /tmp/m3pro_map)
```

## Partie 19b: Afficher la caméra dans le tableau de bord

La caméra du robot est visible en direct dans le tableau de bord. Assurez-vous
que la caméra est lancée:

```bash
ros2 launch slam_mapping app_camera.launch.py
```

Le panneau "Camera Feed" affiche le flux vidéo en temps réel via un flux
MJPEG. Le menu déroulant en haut à droite permet de changer de vue:

```text
Live Camera      → image brute de la caméra RGB
Object Detection → image annotée avec les objets détectés (cercles verts)
Camera Obstacles → image annotée avec les obstacles de profondeur (rectangles rouges)
```

Les vues "Object Detection" et "Camera Obstacles" ne s'affichent que si les
noeuds de détection sont lancés:

```bash
ros2 launch m3pro_teacher_vision detect_and_pick.launch.py pick:=false
```

Comment fonctionne le flux caméra:

```text
Mode "Live Camera":
  Caméra → web_server_node (compresse en JPEG) → flux MJPEG HTTP
  Le navigateur affiche les images JPEG à ~6 FPS

Mode "Object Detection" / "Camera Obstacles":
  Caméra → noeud détection → image annotée → /teacher/detection_image
  rosbridge → WebSocket → navigateur (décode et affiche)
```

Question:

```text
Pourquoi le mode Live Camera utilise HTTP (MJPEG) alors que les
modes détection utilisent WebSocket (rosbridge) ?
```

Réponse:

```text
Le mode live transporte des images brutes de la caméra. Le
web_server_node les compresse en JPEG côté robot et les envoie
comme un flux HTTP standard — c'est simple et efficace.
Les modes détection utilisent des images déjà traitées par ROS,
donc il est naturel de les recevoir via rosbridge qui est déjà
connecté aux topics ROS.
```

Question:

```text
Quelles sont les deux technologies qui permettent au navigateur web
de communiquer avec ROS2 ?
```

Réponse:

```text
1. rosbridge: un pont qui convertit les messages ROS2 en messages
   WebSocket JSON.
2. roslibjs: une bibliothèque JavaScript qui gère le protocole
   WebSocket côté navigateur.
```

## Partie 20: Comprendre l'architecture web

Ouvrez le fichier HTML:

```bash
sed -n '1,30p' /root/m3pro_teacher_ws/src/m3pro_teacher_web/web/index.html
```

Cherchez:

```text
roslib.min.js
ws://${host}:9090
```

Puis regardez comment la carte est affichée:

```bash
sed -n '80,120p' /root/m3pro_teacher_ws/src/m3pro_teacher_web/web/index.html
```

Le schéma:

```text
Navigateur (votre PC)              Jetson (robot)
┌──────────────────┐       ┌──────────────────────┐
│  index.html      │←HTTP→ │  web_server_node     │
│  (roslibjs)      │       │  (port 8080)         │
│                  │← WS → │  rosbridge           │
│                  │       │  (port 9090)         │
└──────────────────┘       └───────┬──────────────┘
                                   │
                           ┌───────▼──────────┐
                           │  Topics ROS2     │
                           │  /map /odom ...  │
                           └──────────────────┘
```

Question:

```text
Pourquoi l'image caméra passe par HTTP (snapshot) plutôt que par
rosbridge ?
```

Réponse:

```text
Envoyer des images non compressées via WebSocket serait trop lent.
Le web_server_node compresse l'image en JPEG côté robot et le
navigateur récupère juste une petite image via HTTP.
```

---

# Partie D: Détection d'objets par caméra

---

## Partie 21: Comprendre la détection par couleur HSV

La détection utilise l'espace colorimétrique HSV au lieu de RGB.

```text
HSV = Hue (teinte), Saturation, Value (luminosité)
```

Pourquoi HSV est meilleur que RGB pour la détection:

```text
En RGB, la couleur rouge change selon l'éclairage:
  lumière forte: (255, 100, 100)
  lumière faible: (100, 40, 40)
  → les valeurs sont très différentes

En HSV, le rouge reste autour de H=0 ou H=170-180:
  lumière forte: (0, 200, 255)
  lumière faible: (0, 200, 100)
  → seul V change, H et S restent similaires
```

Valeurs HSV courantes (sur une échelle de 0-180 pour H en OpenCV):

```text
Rouge   : H = 0-10 ou 170-180, S > 120, V > 70
Vert    : H = 35-85,           S > 100, V > 70
Bleu    : H = 100-130,         S > 120, V > 70
Jaune   : H = 20-35,           S > 100, V > 100
Orange  : H = 10-20,           S > 120, V > 100
```

Question:

```text
Pourquoi le rouge a-t-il deux plages HSV ?
```

Réponse:

```text
Dans l'espace HSV, la teinte (H) est un cercle de 0 à 180. Le rouge
se trouve aux deux extrémités du cercle: autour de 0 et autour de
180. Il faut donc deux masques pour capturer toutes les nuances de
rouge.
```

## Partie 22: Comprendre le code de détection

Ouvrez le fichier du détecteur:

```bash
sed -n '1,50p' /root/m3pro_teacher_ws/src/m3pro_teacher_vision/m3pro_teacher_vision/object_detector_node.py
```

Puis la méthode de détection principale:

```bash
sed -n '100,160p' /root/m3pro_teacher_ws/src/m3pro_teacher_vision/m3pro_teacher_vision/object_detector_node.py
```

Le processus étape par étape:

```text
1. Recevoir une image RGB de la caméra
2. Convertir en HSV:
   hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

3. Créer un masque binaire pour la couleur cible:
   mask = cv2.inRange(hsv, borne_basse, borne_haute)
   → pixels de la bonne couleur = blanc (255)
   → autres pixels = noir (0)

4. Nettoyer le masque:
   morphologyEx(OPEN)  → supprime le bruit (petits points)
   morphologyEx(CLOSE) → bouche les trous

5. Trouver les contours:
   contours = cv2.findContours(mask)

6. Pour chaque contour assez grand:
   → calculer le centroïde (cx, cy) en pixels
   → lire la profondeur à (cx, cy) dans l'image de profondeur
   → convertir en position 3D:
     x = (cx - camera_cx) / fx * profondeur
     y = (cy - camera_cy) / fy * profondeur
     z = profondeur
```

Question:

```text
À quoi servent fx, fy, cx, cy ?
```

Réponse:

```text
Ce sont les paramètres intrinsèques de la caméra. fx et fy sont les
distances focales en pixels. cx et cy sont les coordonnées du centre
optique. Ils permettent de convertir une position en pixels vers une
position en mètres dans l'espace 3D.
```

Question:

```text
Dans quel repère TF est exprimée la position 3D détectée ?
```

Réponse:

```text
camera_color_optical_frame. C'est le repère optique de la caméra où
Z pointe vers l'avant, X vers la droite et Y vers le bas.
```

## Partie 23: Lancer la détection

Assurez-vous que la caméra est lancée. Puis dans un nouveau terminal:

```bash
ros2 launch m3pro_teacher_vision detect_and_pick.launch.py pick:=false
```

Le paramètre `pick:=false` lance la détection seule, sans activer le bras.

Posez un objet rouge devant la caméra (entre 15 cm et 1 m).

## Partie 24: Observer les résultats de détection

Vérifiez dans un terminal:

```bash
ros2 topic echo /teacher/detections
```

Résultat attendu:

```text
header:
  frame_id: camera_color_optical_frame
poses:
- position:
    x: 0.05
    y: 0.12
    z: 0.45
  orientation:
    w: 1.0
```

Cela signifie: un objet détecté à 45 cm de profondeur, légèrement à
droite et en bas du centre de l'image.

Pour voir l'image annotée avec les cercles de détection:

```bash
ros2 run rqt_image_view rqt_image_view /teacher/detection_image
```

Un cercle vert apparaît autour de chaque objet détecté avec la distance
en mètres.

Dans RViz: si les marqueurs sont activés, des sphères rouges apparaissent
à la position 3D des objets détectés.

## Partie 25: Modifier les paramètres de détection

La configuration est dans:

```bash
cat /root/m3pro_teacher_ws/src/m3pro_teacher_vision/config/detection_params.yaml
```

Pour détecter un objet vert au lieu de rouge, modifiez:

```yaml
hsv_low_1: [35, 100, 70]
hsv_high_1: [85, 255, 255]
hsv_low_2: [35, 100, 70]
hsv_high_2: [85, 255, 255]
```

Pour trouver les bonnes valeurs HSV de votre objet:

```text
1. Placez l'objet devant la caméra
2. Faites une capture: ros2 topic echo /camera/color/image_raw --once
3. Ou utilisez rqt_image_view pour observer les couleurs
4. Notez les valeurs H, S, V dominantes
5. Définissez une plage autour de ces valeurs (± 10 pour H, ± 40 pour S et V)
```

Après modification, relancez la détection.

Question:

```text
Que se passe-t-il si min_contour_area est trop petit ?
```

Réponse:

```text
Le détecteur signale du bruit comme des objets. De petites taches de
la bonne couleur dans l'environnement seront détectées à tort.
```

Question:

```text
Que se passe-t-il si min_contour_area est trop grand ?
```

Réponse:

```text
Le détecteur ignore les petits objets ou les objets éloignés qui
apparaissent petits dans l'image.
```

---

# Partie E: Ramassage avec le bras robotique

---

## Partie 26: Comprendre le bras du M3 Pro

Le bras du robot a 6 articulations:

```text
Articulation         Axe    Mouvement
─────────────────────────────────────────────
base_yaw_joint       Z      rotation gauche/droite
shoulder_joint       Y      épaule haut/bas
elbow_joint          Y      coude haut/bas
wrist_pitch_joint    Y      poignet haut/bas
wrist_roll_joint     X      rotation de la pince
left/right_finger    lin.   ouverture de la pince
```

Dimensions du bras (depuis l'URDF):

```text
Bras supérieur : 0.11 m
Avant-bras     : 0.11 m
Poignet+pince  : 0.12 m
Portée totale  : ~0.34 m depuis l'épaule
```

Convention Yahboom:

```text
Les servomoteurs sont commandés en degrés (0 à 180).
90° = position centrale.
Conversion: servo_degrés = radians × (180/π) + 90
```

Question:

```text
Si base_yaw_joint = 120°, dans quelle direction pointe le bras ?
```

Réponse:

```text
120° - 90° = +30° en radians (0.52 rad). Le bras pointe vers la
gauche du robot (environ 30 degrés à gauche du centre).
```

## Partie 27: Comprendre la cinématique inverse

La cinématique inverse (IK) convertit une position 3D souhaitée (x, y, z)
en angles d'articulations.

Ouvrez le code:

```bash
sed -n '220,280p' /root/m3pro_teacher_ws/src/m3pro_teacher_vision/m3pro_teacher_vision/pick_and_place_node.py
```

Le calcul étape par étape:

```text
Étape 1: Rotation de base
  base_yaw = atan2(y, x)
  → Le bras tourne pour pointer vers l'objet

Étape 2: Distance dans le plan du bras
  r = √(x² + y²)     ← distance horizontale
  h = z - hauteur_épaule  ← hauteur relative

Étape 3: IK planaire à 2 segments (épaule + coude)
  On cherche les angles θ1 (épaule) et θ2 (coude)
  pour que les deux segments L1 et L2 atteignent le point (r, h).

  Théorème d'Al-Kashi (loi des cosinus):
  cos(θ2) = (L1² + L2² - d²) / (2 × L1 × L2)
  θ1 = atan2(h, r) + acos((L1² + d² - L2²) / (2 × L1 × d))

Étape 4: Compensation du poignet
  wrist_pitch = -(θ1 + θ2) - π/2
  → La pince pointe vers le bas pour saisir l'objet au sol
```

Question:

```text
Pourquoi le poignet doit-il compenser les angles de l'épaule et du
coude ?
```

Réponse:

```text
Si l'épaule et le coude sont inclinés, la pince sera inclinée aussi.
Pour que la pince pointe droit vers le bas, il faut que le poignet
compense en ajoutant l'angle opposé.
```

Question:

```text
Quand la fonction compute_ik retourne-t-elle None ?
```

Réponse:

```text
Quand l'objet est hors de portée du bras, c'est-à-dire quand la
distance est plus grande que L1 + L2 ou quand un angle dépasse les
limites d'articulation (±1.57 radians).
```

## Partie 28: Comprendre la machine à états

Le ramassage fonctionne avec une machine à états:

```text
     IDLE ─── objet détecté ───→ APPROACH
      ↑                              │
      │                     conduire vers l'objet
      │                              │
      │                              ▼
    DONE ← ouvrir pince ── LIFT    REACH
                              ↑      │
                              │  bras vers l'objet
                              │      │
                            GRASP ←──┘
                         fermer pince
```

Ouvrez le code:

```bash
sed -n '130,180p' /root/m3pro_teacher_ws/src/m3pro_teacher_vision/m3pro_teacher_vision/pick_and_place_node.py
```

Cherchez:

```text
State.IDLE
State.APPROACH
State.REACH
State.GRASP
State.LIFT
State.DONE
```

Question:

```text
Que fait le robot dans l'état APPROACH ?
```

Réponse:

```text
Le robot publie des commandes /cmd_vel pour rouler vers l'objet
détecté. Il s'arrête quand il est à approach_distance (30 cm par
défaut) de l'objet.
```

Question:

```text
Pourquoi le robot ne ramasse-t-il pas directement? Pourquoi d'abord
s'approcher ?
```

Réponse:

```text
Le bras a une portée limitée (~34 cm). Le robot doit d'abord
s'approcher suffisamment pour que l'objet soit à portée du bras.
```

## Partie 29: Lancer le ramassage (avec autorisation de l'enseignant)

IMPORTANT: demandez l'autorisation à l'enseignant avant cette étape.
Le bras va bouger physiquement.

Assurez-vous que ces éléments tournent:

```text
[OK] Yahboom bringup (lidar + odométrie + caméra + driver bras)
[OK] robot_state_publisher (URDF)
```

Lancez la détection avec le ramassage activé:

```bash
ros2 launch m3pro_teacher_vision detect_and_pick.launch.py
```

Posez un objet rouge au sol devant le robot (entre 30 cm et 1 m).

Ce que vous devez voir:

```text
1. Le détecteur affiche "Detected 1 object(s), nearest at ..."
2. Le pick_and_place affiche "Target acquired ... Approaching..."
3. Le robot roule lentement vers l'objet
4. "State: APPROACH -> REACH" → le bras se déploie
5. "State: REACH -> GRASP" → la pince se ferme
6. "State: GRASP -> LIFT" → le bras se relève
7. "State: LIFT -> DONE" → la pince s'ouvre, retour au repos
```

Observez les logs:

```bash
# Dans un autre terminal:
ros2 topic echo /teacher/detections
```

Si le bras ne bouge pas physiquement mais que les logs affichent
`[DRY RUN]`, cela signifie que le paquet `arm_msgs` n'est pas installé
ou que le topic de commande est différent.

## Partie 30: Trouver le bon topic de commande du bras

```bash
ros2 topic list | grep -i arm
```

Cherchez un topic de commande (pas `/arm6_joints` qui est en lecture).

Possibilités courantes:

```text
/arm_control
/servo_control
/arm_command
```

Pour voir ce que le driver du robot attend:

```bash
ros2 node list
ros2 node info /yahboomcar_driver
```

Cherchez la section "Subscribers" pour trouver le bon topic.

Si nécessaire, modifiez dans la configuration:

```bash
# Éditez config/detection_params.yaml
# Changez arm_command_topic pour le bon topic
```

## Partie 31: Ajuster les paramètres de la pince

La pince utilise des valeurs en degrés de servomoteur:

```text
gripper_open_value: 30    → pince grande ouverte
gripper_close_value: 75   → pince fermée sur un objet
```

Si la pince ne serre pas assez:

```text
Augmentez gripper_close_value (ex: 80 ou 85)
Attention: ne dépassez pas 90 pour ne pas forcer le servomoteur
```

Si la pince serre trop fort:

```text
Diminuez gripper_close_value (ex: 65 ou 70)
```

---

# Partie F: Intégration complète

---

## Partie 32: Tout lancer ensemble

Ouvrez quatre terminaux Docker. Dans chacun, sourcez les workspaces.

Terminal 1 — bringup:

```bash
bash /home/jetson/start_agent.sh
```

Terminal 2 — SLAM + navigation:

```bash
ros2 launch m3pro_teacher_nav slam_and_nav.launch.py
```

Terminal 3 — tableau de bord web:

```bash
ros2 launch m3pro_teacher_web web_dashboard.launch.py
```

Terminal 4 — détection + ramassage:

```bash
ros2 launch m3pro_teacher_vision detect_and_pick.launch.py
```

Ouvrez le tableau de bord: `http://10.10.221.123:8080`

Ce que vous pouvez faire:

```text
1. Envoyer le robot explorer une zone en cliquant sur la carte web
2. Le robot construit la carte en roulant
3. Quand il voit un objet rouge au sol, il s'arrête et le ramasse
4. Après le ramassage, il retourne en état IDLE et peut recevoir
   de nouveaux objectifs
```

## Partie 33: Scénario d'exercice

Exercice guidé:

```text
1. Placez 3 objets rouges dans la salle à des positions différentes
2. Lancez le système complet (Partie 32)
3. Envoyez le robot vers le premier objet via le tableau de bord
4. Observez le robot le détecter et le ramasser
5. Envoyez le robot vers le deuxième objet
6. Notez combien de temps prend chaque ramassage
7. Le robot arrive-t-il à fermer la boucle sur la carte?
```

Questions de synthèse:

```text
Listez tous les repères TF dans la chaîne complète, de la carte
jusqu'à la pince du robot.
```

Réponse:

```text
map → odom → base_link → arm_base_link →
shoulder_pan_link → upper_arm_link → forearm_link →
wrist_pitch_link → wrist_roll_link → gripper_palm_link →
left_finger_link / right_finger_link

Et aussi:
base_link → camera_link → camera_color_optical_frame
base_link → scan0_frame / scan1_frame
```

```text
Quels noeuds publient sur /cmd_vel et pourquoi ?
```

Réponse:

```text
1. teleop_twist_keyboard → quand on conduit manuellement
2. Nav2 controller_server → pendant la navigation autonome
3. pick_and_place_node → pendant la phase APPROACH

Un seul doit publier à la fois sinon les commandes se mélangent.
```

```text
Que se passe-t-il si quelqu'un passe devant le robot pendant la
navigation ?
```

Réponse:

```text
Le lidar détecte la personne comme un obstacle dans la costmap locale.
Le contrôleur local recalcule un chemin pour contourner la personne.
Si le passage est complètement bloqué, le behavior_server peut faire
reculer le robot ou attendre.
```

---

# Partie G: Nettoyage

---

## Partie 34: Arrêter tous les programmes

Arrêtez chaque terminal avec `Ctrl-C` dans l'ordre inverse:

```text
1. Ctrl-C dans le terminal détection + ramassage
2. Ctrl-C dans le terminal web
3. Ctrl-C dans le terminal SLAM/navigation
4. Ctrl-C dans le terminal bringup (dernier)
```

Vérifiez qu'il ne reste aucun processus:

```bash
ps -ef | grep -E 'slam_toolbox|nav2|rviz2|m3pro_teacher|rosbridge' | grep -v grep
```

S'il reste des processus:

```bash
pkill -TERM -f slam_toolbox
pkill -TERM -f rviz2
pkill -TERM -f rosbridge
```

Vérifiez que le robot est arrêté:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0}, angular: {z: 0.0}}"
```

Ramenez le bras à la position repos:

```bash
ros2 topic pub --once /arm6_joints arm_msgs/msg/ArmJoints \
  "{joint1: 90, joint2: 120, joint3: 10, joint4: 20, joint5: 90, joint6: 30, time: 700}"
```

---

# Défis bonus

Choisissez un ou plusieurs défis:

1. **Patrouille automatique**: Écrivez un script Python qui envoie une
   séquence de 4 objectifs de navigation en boucle. Le robot doit
   patrouiller continuellement entre ces points.

2. **Multi-couleur**: Modifiez la détection pour reconnaître à la fois les
   objets rouges et les objets verts. Affichez la couleur détectée dans les
   logs.

3. **Zone de dépôt**: Au lieu de lâcher l'objet sur place, modifiez le code
   pour que le robot transporte l'objet vers un point fixe de la carte
   (zone de dépôt) avant de le lâcher.

4. **Dashboard amélioré**: Ajoutez un compteur d'objets ramassés dans le
   tableau de bord web. Indice: créez un topic `/teacher/pick_count` et
   abonnez-vous dans le JavaScript.

5. **Exploration autonome**: Écrivez un noeud qui analyse la carte en cours
   de construction pour trouver les frontières (limites entre zones connues
   et inconnues) et envoie automatiquement le robot explorer ces zones.
