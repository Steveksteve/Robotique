<?php

<?php

require_once __DIR__ . '/MissionController.php';

$router->add('GET', '/missions', ['MissionController', 'index']);
$router->add('POST', '/missions', ['MissionController', 'store']);

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