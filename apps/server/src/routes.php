<?php

// GET simple
$router->get('/', function() {
    header('Content-Type: application/json');
    echo json_encode(["message" => "Hello depuis le serveur robotique !"]);
});

// POST pour commander le robot
$router->post('/', function() {
    header('Content-Type: application/json');
    echo json_encode(["status" => "Commande robot reçue"]);
});