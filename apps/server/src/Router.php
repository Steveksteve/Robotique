<?php

class Router {
    private $routes = [];

    public function get($path, $callback) {
        $this->routes['GET'][$path] = $callback;
    }

    public function post($path, $callback) {
        $this->routes['POST'][$path] = $callback;
    }

    public function patch($path, $callback) {
        $this->routes['PATCH'][$path] = $callback;
    }

    public function put($path, $callback) {
        $this->routes['PUT'][$path] = $callback;
    }

    public function run() {
        $method = $_SERVER['REQUEST_METHOD'];
        $uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

        $script_name = dirname($_SERVER['SCRIPT_NAME']);
        if ($script_name !== '/' && str_starts_with($uri, $script_name)) {
            $uri = substr($uri, strlen($script_name));
        }

        if ($uri === false || $uri === '') {
            $uri = '/';
        }

        if ($uri[0] !== '/') {
            $uri = '/' . $uri;
        }

        $matched = false;

        if (isset($this->routes[$method])) {
            foreach ($this->routes[$method] as $path => $callback) {
                // Convert path with {param} to regex
                $pattern = preg_replace('#\{[^/]+\}#', '([^/]+)', $path);
                $pattern = '#^' . $pattern . '$#';

                if (preg_match($pattern, $uri, $matches)) {
                    array_shift($matches); // remove full match
                    $matched = true;

                    if (is_array($callback)) {
                        call_user_func_array([$callback[0], $callback[1]], $matches);
                    } else {
                        call_user_func_array($callback, $matches);
                    }

                    break;
                }
            }
        }

        if (! $matched) {
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
