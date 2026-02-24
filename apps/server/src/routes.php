<?php

$router->get('/', function() {
    header('Content-Type: application/json');
    echo json_encode(["message" => "Hello depuis le serveur robotique !"]);
});

$router->post('/', function() {
    header('Content-Type: application/json');
    echo json_encode(["status" => "Commande robot reçue"]);
});