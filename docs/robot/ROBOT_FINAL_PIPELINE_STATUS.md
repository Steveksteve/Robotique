# État des essais sur le robot

Cette page décrit le résultat réellement obtenu sur le robot et les opérations nécessaires pour reproduire la démonstration.

## Résultat validé

| Élément | État | Observation |
| --- | --- | --- |
| Stack Docker sur le PC | ✅ Validé | API, frontend et WebSocket accessibles |
| Faux robot | ✅ Validé | Mission complète jusqu’à `COMPLETED` |
| Connexion du robot réel au PC | ✅ Validé | Le client ROS 2 communique avec le WebSocket |
| Build du workspace ROS 2 | ✅ Validé | Les packages sont construits et disponibles |
| Mission sur robot en `dry_run` | ✅ Validé | Scénario complet sans mouvement physique |
| Navigation réelle Nav2 | ✅ Validé | Déplacement entre les zones de prise et de dépose |
| Lecture du QR réel | ✅ Validé | Le QR attendu est lu pendant la mission |
| Prise et dépose réelles | ✅ Validé | Le bras saisit puis dépose l’objet après calibrage de la pince |
| Mission réelle complète | ✅ Validé | Navigation, QR, prise, transport et dépose jusqu’à `COMPLETED` |

## Contraintes de préparation

Le système fonctionne de bout en bout, mais son démarrage n’est pas encore entièrement automatisé.

Avant chaque démonstration, il faut :

1. démarrer la stack Docker sur le PC ;
2. relancer les nœuds ROS 2 nécessaires sur le robot, notamment le bringup, la caméra, Nav2, le contrôle du bras et l’exécuteur de mission ;
3. vérifier que les topics et services attendus sont disponibles ;
4. ajuster la valeur de fermeture de la pince selon l’objet utilisé ;
5. effectuer un court test de prise avant de lancer la mission complète.

Ces opérations sont des étapes de mise en route et de calibrage. Elles ne signifient pas que la mission est partielle ou bloquée.

## Vérifications rapides avant une mission

```bash
ros2 node list
ros2 topic list
ros2 service list | grep /arm
ros2 topic hz /camera/color/image_raw/compressed
```

La chaîne TF attendue est :

```text
map → odom → base_link
```

## Calibrage de la pince

La pince est commandée en degrés de servomoteur. Dans le code actuel, la fermeture est notamment définie par :

- le paramètre `gripper_close` du nœud de contrôle manuel ;
- le paramètre `gripper_close_value` du nœud de prise et dépose.

La valeur par défaut est proche de `75`, mais elle doit être adaptée à la taille, à la rigidité et à la position de l’objet. Une valeur trop faible ne maintient pas correctement l’objet ; une valeur trop forte peut faire forcer le servomoteur.

Exemple de test manuel :

```bash
ros2 service call /arm/set_gripper \
  m3pro_teacher_interfaces/srv/SetJoint \
  "{value: 75.0}"
```

Il faut commencer avec une valeur prudente, observer la prise, puis modifier progressivement la valeur retenue pour la démonstration.

## Lancement de la mission

Mode de contrôle sans mouvement :

```bash
ros2 launch m3pro_teacher_vision mission_mvp.launch.py \
  api_base:=http://<IP_DU_PC>:8000 \
  ws_url:=ws://<IP_DU_PC>:8765 \
  robot_id:=raa-robot-01 \
  dry_run:=true \
  simulated_qr:=a
```

Mode réel :

```bash
ros2 launch m3pro_teacher_vision mission_mvp.launch.py \
  api_base:=http://<IP_DU_PC>:8000 \
  ws_url:=ws://<IP_DU_PC>:8765 \
  robot_id:=raa-robot-01 \
  dry_run:=false \
  camera_topic:=/camera/color/image_raw/compressed
```

Pendant l’essai, une personne doit conserver un accès immédiat à l’arrêt matériel et au bouton **Stop** du dashboard.

## Améliorations prévues

- regrouper le lancement des nœuds dans une seule commande ou un fichier `launch` principal ;
- charger la valeur de fermeture de la pince depuis une configuration propre à l’objet ;
- ajouter une vérification automatique des topics et services avant le départ de la mission.
