<?php

class Database
{
    private static function env($key, $default = null)
    {
        $val = getenv($key);
        return $val === false ? $default : $val;
    }

    public static function connect()
    {
        $host = self::env('DB_HOST', 'localhost');
        $dbname = self::env('DB_NAME', 'raa_db');
        $username = self::env('DB_USER', 'root');
        $password = self::env('DB_PASSWORD', '');

        try {
            $pdo = new PDO(
                "mysql:host=" . $host . ";dbname=" . $dbname . ";charset=utf8mb4",
                $username,
                $password
            );

            $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

            return $pdo;

        } catch (PDOException $e) {
            http_response_code(500);
            header('Content-Type: application/json');
            echo json_encode([
                'error' => 'Impossible de se connecter à la base de données.'
            ]);
            exit;
        }
    }
}