<?php

header("Content-Type: application/json");

require_once __DIR__ . "/../src/database.php";

$query = $pdo->query("
    SELECT
        rl.id,
        rl.mission_id,
        rl.robot_x,
        rl.robot_y,
        rl.timestamp,
        m.status
    FROM robot_logs rl
    INNER JOIN missions m
        ON m.id = rl.mission_id
    ORDER BY rl.timestamp DESC
");

$logs = $query->fetchAll(PDO::FETCH_ASSOC);

echo json_encode($logs);