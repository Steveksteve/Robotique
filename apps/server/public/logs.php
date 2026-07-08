<?php

header('Access-Control-Allow-Origin: *');
header('Content-Type: application/json');

require_once __DIR__ . '/../src/Database.php';

$pdo = Database::connect();
$query = $pdo->query("
    SELECT
        rl.id,
        rl.mission_id,
        rl.robot_id,
        rl.robot_x,
        rl.robot_y,
        rl.status,
        rl.message,
        rl.timestamp,
        m.status AS mission_status
    FROM robot_logs rl
    LEFT JOIN missions m ON m.id = rl.mission_id
    ORDER BY rl.timestamp DESC
");

echo json_encode($query->fetchAll(PDO::FETCH_ASSOC));
