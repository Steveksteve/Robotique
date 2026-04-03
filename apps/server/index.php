<?php

require_once __DIR__ . '/Router.php';

$router = new Router();

require_once __DIR__ . '/src/routes.php';

$router->run();