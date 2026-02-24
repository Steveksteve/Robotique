<?php

class Router {
    private $routes = [];

    public function get($path, $callback) {
        $this->routes['GET'][$path] = $callback;
    }

    public function post($path, $callback) {
        $this->routes['POST'][$path] = $callback;
    }

    public function run() {
        $method = $_SERVER['REQUEST_METHOD'];

        $uri = '/';

        if (isset($this->routes[$method][$uri])) {
            call_user_func($this->routes[$method][$uri]);
        } else {
            http_response_code(200);
            echo json_encode(["message" => "Bienvenue sur le serveur robotique !"]);
        }
    }
}