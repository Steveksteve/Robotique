<?php

require_once __DIR__ . "/Database.php";
require_once __DIR__ . "/MissionController.php";

$pdo = Database::connect();
$controller = new MissionController($pdo);

$method = $_SERVER["REQUEST_METHOD"];
$uri = parse_url($_SERVER["REQUEST_URI"], PHP_URL_PATH);

$basePath = rtrim(str_replace("\\", "/", dirname($_SERVER["SCRIPT_NAME"])), "/");

if ($basePath !== "" && $basePath !== "/" && str_starts_with($uri, $basePath)) {
    $uri = substr($uri, strlen($basePath));
}

if (str_starts_with($uri, "/index.php")) {
    $uri = substr($uri, strlen("/index.php"));
}

$uri = preg_replace('#/+#', '/', $uri);

if ($uri === "" || $uri === false) {
    $uri = "/";
}

if ($uri === "/" && $method === "GET") {
    echo json_encode([
        "status" => "ok",
        "service" => "api"
    ]);
    exit;
}

if ($uri === "/missions" && $method === "GET") {
    $controller->index();
    exit;
}

if (preg_match("#^/missions/(\d+)$#", $uri, $matches) && $method === "GET") {
    $controller->show($matches[1]);
    exit;
}

if ($uri === "/missions" && $method === "POST") {
    $controller->store();
    exit;
}

if (preg_match("#^/missions/(\d+)/status$#", $uri, $matches) && $method === "PATCH") {
    $controller->updateStatus($matches[1]);
    exit;
}

if (preg_match("#^/missions/(\d+)$#", $uri, $matches) && $method === "DELETE") {
    $controller->delete($matches[1]);
    exit;
}

if ($uri === "/logs" && $method === "GET") {

    $stmt = $pdo->query("
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

    echo json_encode($stmt->fetchAll());

    exit;
}
echo json_encode([
    "error" => "Route not found",
    "method" => $method,
    "uri" => $uri
]);