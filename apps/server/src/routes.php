<?php

require_once __DIR__ . '/MissionController.php';

$router->get('/missions', ['MissionController', 'index']);
$router->post('/missions', ['MissionController', 'store']);
$router->patch('/missions/{id}/status', ['MissionController', 'updateStatus']);

$router->get('/', function() {
    header('Content-Type: application/json');
    echo json_encode([
        'message' => 'Hello depuis le serveur robotique'
    ]);
});

$router->post('/', function() {
    header('Content-Type: application/json');
    echo json_encode([
        'status' => 'Commande robot reçue'
    ]);
});