# Guide d’exécution du MVP

Ce guide décrit le chemin utilisé pour la démonstration finale. Les commandes historiques de l’exercice SLAM et les anciennes variantes Docker ont été retirées pour éviter les doublons.

## 1. Démarrer la stack sur le PC

Depuis la racine du dépôt :

```bash
docker compose -f docker-compose.realtime.yml up --build -d
```

Vérifications :

```bash
curl http://localhost:8000/health
curl -I http://localhost:8080
```

Adresses utilisées :

- dashboard : `http://localhost:8080` ;
- API : `http://localhost:8000` ;
- WebSocket : `ws://localhost:8765`.

Pour voir les logs :

```bash
docker compose -f docker-compose.realtime.yml logs -f
```

## 2. Vérifier le scénario avec le faux robot

```bash
python -m pip install websockets
python tests/manual/fake_robot.py
```

Dans le dashboard :

1. créer une mission ;
2. vérifier que le QR attendu correspond à `a` ;
3. affecter la mission au robot `raa-fake-robot-01` ;
4. suivre les statuts jusqu’à `COMPLETED`.

Ce test valide l’interface, l’API, la base et le WebSocket, mais pas le matériel ROS 2.

## 3. Préparer le robot

Les exemples ci-dessous supposent que le workspace est installé dans `/root/m3pro_teacher_ws` à l’intérieur du conteneur ROS 2 du robot.

```bash
source /opt/ros/humble/setup.bash
source /root/yahboomcar_ws/install/setup.bash 2>/dev/null || true
source /root/M3Pro_ws/install/setup.bash 2>/dev/null || true
source /root/m3pro_teacher_ws/install/setup.bash
```

Vérifier les packages :

```bash
ros2 pkg list | grep m3pro_teacher
```

Le bringup Yahboom doit être lancé avant la mission afin de publier les capteurs, l’odométrie et les commandes du robot. À chaque redémarrage ou nouvelle session, relancer et vérifier l’ensemble des nœuds nécessaires : bringup, caméra, Nav2, contrôle du bras et exécuteur de mission. Le démarrage n’est pas encore regroupé dans une commande unique.

## 4. Valider d’abord en `dry_run`

Remplacer `<IP_DU_PC>` par l’adresse du PC qui exécute Docker :

```bash
ros2 launch m3pro_teacher_vision mission_mvp.launch.py \
  api_base:=http://<IP_DU_PC>:8000 \
  ws_url:=ws://<IP_DU_PC>:8765 \
  robot_id:=raa-robot-01 \
  dry_run:=true \
  simulated_qr:=a
```

Créer puis affecter une mission depuis le dashboard. La mission doit parcourir tous les états sans déplacer le robot.

## 5. Vérifier la navigation

Avant un essai réel, vérifier la chaîne TF :

```bash
ros2 run tf2_ros tf2_echo odom base_link
ros2 run tf2_ros tf2_echo map odom
```

La chaîne attendue est :

```text
map → odom → base_link
```

Lancer Nav2 avec la carte retenue :

```bash
ros2 launch m3pro_teacher_nav navigation.launch.py \
  map:=/root/m3pro_teacher_ws/src/m3pro_teacher_nav/maps/salle.yaml \
  rviz:=true
```

Dans RViz, fournir la pose initiale avant d’envoyer un objectif.

## 6. Vérifier le flux caméra et le QR

Lister les topics disponibles :

```bash
ros2 topic list | grep -i camera
```

Vérifier qu’un topic reçoit réellement des images :

```bash
ros2 topic info /camera/color/image_raw/compressed -v
ros2 topic hz /camera/color/image_raw/compressed
```

Tester le lecteur QR :

```bash
ros2 run m3pro_teacher_vision qr_code_reader_node \
  --ros-args -p camera_topic:=/camera/color/image_raw/compressed
```

Puis appeler son service :

```bash
ros2 service call /qr/read std_srvs/srv/Trigger "{}"
```

Ne pas passer en mode réel tant que le topic ne publie pas d’images et que le QR n’est pas détecté de manière répétable.

## 7. Calibrer la pince

Avant chaque démonstration, tester la fermeture de la pince avec l’objet réellement utilisé :

```bash
ros2 service call /arm/set_gripper \
  m3pro_teacher_interfaces/srv/SetJoint \
  "{value: 75.0}"
```

La valeur `75.0` est un point de départ. L’ajuster progressivement afin que l’objet soit maintenu sans faire forcer le servomoteur. La valeur retenue doit ensuite correspondre au paramètre `gripper_close` ou `gripper_close_value`, selon le nœud utilisé.

## 8. Lancer une mission réelle

Après validation de Nav2, de la caméra et du bras :

```bash
ros2 launch m3pro_teacher_vision mission_mvp.launch.py \
  api_base:=http://<IP_DU_PC>:8000 \
  ws_url:=ws://<IP_DU_PC>:8765 \
  robot_id:=raa-robot-01 \
  dry_run:=false \
  camera_topic:=/camera/color/image_raw/compressed
```

Pendant l’essai :

- conserver un accès direct à l’arrêt matériel du robot ;
- garder le bouton **Stop** visible dans le dashboard ;
- dégager la zone autour du robot et du bras ;
- commencer à vitesse réduite ;
- arrêter immédiatement le test si les capteurs ou la communication deviennent instables.

## 9. Arrêt propre

Arrêter les commandes ROS 2 avec `Ctrl+C`, puis publier une vitesse nulle si nécessaire :

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0}, angular: {z: 0.0}}"
```

Sur le PC :

```bash
docker compose -f docker-compose.realtime.yml down
```

## Dépannage rapide

| Symptôme | Vérification |
| --- | --- |
| L’API ne répond pas | `docker compose ... ps` puis logs du service `api` |
| Le dashboard reste hors ligne | vérifier le port `8765` et les logs `realtime` |
| Le robot ne reçoit pas la mission | vérifier `robot_id`, `ws_url` et le message d’identification |
| `Frame [map] does not exist` | lancer Nav2 et définir la pose initiale dans RViz |
| Le QR n’est jamais détecté | vérifier le publisher et la fréquence du topic caméra |
| La pince ne tient pas l’objet | ajuster progressivement `gripper_close` ou `gripper_close_value` |
| Un service ROS 2 manque | relancer le nœud correspondant et contrôler `ros2 node list` / `ros2 service list` |
| La mission passe à `ERROR` | consulter `error_reason`, les événements du dashboard et `GET /logs` |
