<?php

require_once __DIR__ . '/MissionController.php';

$router->add('GET', '/missions', ['MissionController', 'index']);
$router->add('POST', '/missions', ['MissionController', 'store']);