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

if ($uri === "" || $uri === false) {
    $uri = "/";
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

http_response_code(404);
echo json_encode([
    "error" => "Route not found",
    "method" => $method,
    "uri" => $uri
]);