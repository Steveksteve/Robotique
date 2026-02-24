<?php

require_once __DIR__ . '/MissionController.php';

$router->add('GET', '/api/missions', ['MissionController', 'index']);
$router->add('POST', '/api/missions', ['MissionController', 'store']);
