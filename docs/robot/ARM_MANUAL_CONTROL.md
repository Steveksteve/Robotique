# Contrôle Manuel du Bras Yahboom M3 Pro

##  Vue d'Ensemble

Le node `arm_manual_control_node` permet de contrôler chaque articulation du bras du robot M3 Pro de manière indépendante via des services ROS2.

**Convention Yahboom** :
- Plage : 0-180 degrés
- Centre (position neutre) : 90 degrés
- Tous les angles sont en convention servo (pas en radians)

## Architecture

### Topics
- **Publication** : `/arm6_joints` (message `ArmJoints`)
  - Les commandes sont publiées directement au driver du bras

### Services ROS2

#### Contrôle Individual des Joints
```
/arm/set_joint1     (base_yaw)       : SetJoint service
/arm/set_joint2     (shoulder)       : SetJoint service
/arm/set_joint3     (elbow)          : SetJoint service
/arm/set_joint4     (wrist_pitch)    : SetJoint service
/arm/set_joint5     (wrist_roll)     : SetJoint service
/arm/set_gripper    (gripper)        : SetJoint service
```

#### Contrôle Multiple
```
/arm/set_all_joints : SetJoints service (6 values)
```

#### Poses Prédéfinies
```
/arm/home           : Home service (move to home position)
/arm/gripper_open   : Trigger service
/arm/gripper_close  : Trigger service
```

##  Utilisation

### 1. Lancer le Node

```bash
cd m3pro_teacher_ws
colcon build --symlink-install --packages-select m3pro_teacher_interfaces m3pro_teacher_demos
source install/setup.bash

# Lancer le node de contrôle
ros2 run m3pro_teacher_demos arm_manual_control_node
```

### 2. Contrôler le Bras via Services

#### Via ROS2 CLI

```bash
# Déplacer un joint spécifique (base_yaw à 120°)
ros2 service call /arm/set_joint1 m3pro_teacher_interfaces/srv/SetJoint "{value: 120.0}"

# Déplacer le shoulder à 100°
ros2 service call /arm/set_joint2 m3pro_teacher_interfaces/srv/SetJoint "{value: 100.0}"

# Fermer le gripper (angle 75°)
ros2 service call /arm/set_gripper m3pro_teacher_interfaces/srv/SetJoint "{value: 75.0}"

# Déplacer tous les joints à la fois
ros2 service call /arm/set_all_joints m3pro_teacher_interfaces/srv/SetJoints "{values: [90.0, 120.0, 10.0, 20.0, 90.0, 60.0]}"

# Revenir à la position home
ros2 service call /arm/home m3pro_teacher_interfaces/srv/Home "{}"

# Ouvrir le gripper (rapide)
ros2 service call /arm/gripper_open std_srvs/srv/Trigger "{}"

# Fermer le gripper (rapide)
ros2 service call /arm/gripper_close std_srvs/srv/Trigger "{}"
```

### 3. Utiliser le Script CLI

Un script Python simple pour contrôler le bras :

```bash
# Se placer dans le répertoire du workspace
cd m3pro_teacher_ws
source install/setup.bash

# Exemples d'utilisation
python3 src/m3pro_teacher_demos/scripts/arm_control_cli.py joint1 120.0
python3 src/m3pro_teacher_demos/scripts/arm_control_cli.py joint2 100.0
python3 src/m3pro_teacher_demos/scripts/arm_control_cli.py gripper 60.0
python3 src/m3pro_teacher_demos/scripts/arm_control_cli.py all 90 120 10 20 90 60
python3 src/m3pro_teacher_demos/scripts/arm_control_cli.py home
python3 src/m3pro_teacher_demos/scripts/arm_control_cli.py open
python3 src/m3pro_teacher_demos/scripts/arm_control_cli.py close
```

### Dashboard Web

Le dashboard contient un panneau **Arm** qui appelle les services `/arm/*` via rosbridge.

```bash
ros2 launch m3pro_teacher_demos live_showcase.launch.py
ros2 launch m3pro_teacher_web web_dashboard.launch.py
```

### 4. Utiliser en Python

```python
import rclpy
from m3pro_teacher_interfaces.srv import SetJoint, SetJoints, Home

rclpy.init()
node = rclpy.create_node("arm_client")

# Créer un client pour SetJoint
client = node.create_client(SetJoint, "/arm/set_joint1")
client.wait_for_service()

# Créer une requête
request = SetJoint.Request()
request.value = 120.0

# Envoyer la requête
future = client.call_async(request)
rclpy.spin_until_future_complete(node, future)

# Récupérer la réponse
response = future.result()
print(response.message)

rclpy.shutdown()
```

##  Positions de Référence

### Position Home (par défaut)
```
Joint 1 (base_yaw):    90.0°
Joint 2 (shoulder):    120.0°
Joint 3 (elbow):       10.0°
Joint 4 (wrist_pitch): 20.0°
Joint 5 (wrist_roll):  90.0°
Gripper:               60.0° (ouvert)
```

### Positions du Gripper
```
Ouvert:   30.0° (par défaut)
Fermé:    75.0° (par défaut)
```

##  Configuration

Le node utilise des paramètres ROS2 pour la configuration :

```yaml
arm_manual_control_node:
  ros__parameters:
    arm_control_topic: "/arm6_joints"
    home_joint1: 90.0
    home_joint2: 120.0
    home_joint3: 10.0
    home_joint4: 20.0
    home_joint5: 90.0
    home_joint6: 60.0        # Position gripper à home
    gripper_open: 30.0
    gripper_close: 75.0
```

## Debug

### Vérifier que le node fonctionne

```bash
# Dans un terminal, lancer le node
ros2 run m3pro_teacher_demos arm_manual_control_node

# Dans un autre terminal, lister les services disponibles
ros2 service list | grep arm

# Vous devriez voir:
# /arm/gripper_close
# /arm/gripper_open
# /arm/home
# /arm/set_all_joints
# /arm/set_joint1
# /arm/set_joint2
# /arm/set_joint3
# /arm/set_joint4
# /arm/set_joint5
# /arm/set_gripper
```

### Voir les logs

```bash
# Démarrer le node avec verbose
ros2 run m3pro_teacher_demos arm_manual_control_node --ros-args --log-level DEBUG
```

### Écouter les commandes publiées

```bash
# Écouter le topic /arm6_joints
ros2 topic echo /arm6_joints
```

##  Notes Importantes

1. **Sécurité** : Toujours tester les limites de mouvement du bras avant d'utiliser en production
2. **Validation** : Les angles sont automatiquement limités entre 0 et 180°
3. **Convention Yahboom** : Ne pas confondre avec la convention ROS standard (radians)
4. **Gripper** : La valeur 90° = gripper au centre; < 90° = plus ouvert, > 90° = plus fermé

## Dépannage

### Les services ne sont pas disponibles
```
→ Vérifier que le workspace a été compilé: colcon build --symlink-install
→ Vérifier que le sourcing a été fait: source install/setup.bash
```

### Le bras ne bouge pas
```
→ Vérifier que le driver Yahboom est lancé (devrait recevoir les messages sur /arm6_joints)
→ Vérifier les logs du node: ros2 run ... --ros-args --log-level DEBUG
→ Vérifier que arm_msgs est disponible: pip install yahboom-arm-msgs (ou équivalent)
```

### Erreurs de compilation
```
→ Nettoyer et recompiler: colcon build --symlink-install --packages-select m3pro_teacher_interfaces m3pro_teacher_demos
```
