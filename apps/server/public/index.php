<?php

require_once __DIR__ . '/../src/Router.php';

$router = new Router();

require __DIR__ . '/../src/routes.php';

$router->run();