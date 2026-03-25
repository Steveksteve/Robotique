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
        $uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

        $script_name = dirname($_SERVER['SCRIPT_NAME']); 
        $uri = substr($uri, strlen($script_name));

        if ($uri === false || $uri === '') {
            $uri = '/';
        }

        if (isset($this->routes[$method][$uri])) {
            $callback = $this->routes[$method][$uri];

            if (is_array($callback)) {
                call_user_func([$callback[0], $callback[1]]);
            } else {
                call_user_func($callback);
            }
        } else {
            http_response_code(404);
            header('Content-Type: application/json');
            echo json_encode([
                "error" => "Route not found",
                "method" => $method,
                "uri" => $uri
            ]);
        }
    }
}