<?php

class Router
{
    private array $routes = [];

    public function add(string $method, string $path, $callback): void
    {
        $this->routes[] = [
            'method' => $method,
            'path' => $path,
            'callback' => $callback
        ];
    }

    public function run(): void
    {
        $method = $_SERVER['REQUEST_METHOD'];
        $uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

        foreach ($this->routes as $route) {
            if ($route['method'] === $method && $route['path'] === $uri) {
                call_user_func($route['callback']);
                return;
            }
        }

        http_response_code(404);
        echo json_encode([
            'success' => false,
            'message' => 'Route not found.'
        ]);
    }
}