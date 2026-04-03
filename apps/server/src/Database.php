<?php

class Database
{
<<<<<<< HEAD
    private static $host = '127.0.0.1';
    private static $dbname = 'raa';
    private static $username = 'root';
    private static $password = 'TON_MOT_DE_PASSE_ICI'; // Mets ton vrai mot de passe
=======
    private static function env($key, $default = null)
    {
        $val = getenv($key);
        return $val === false ? $default : $val;
    }
>>>>>>> origin/main

    public static function connect()
    {
        $host = self::env('DB_HOST', 'localhost');
        $dbname = self::env('DB_NAME', 'raa_db');
        $username = self::env('DB_USER', 'root');
        $password = self::env('DB_PASSWORD', '');

        try {
            $pdo = new PDO(
<<<<<<< HEAD
                "mysql:host=" . self::$host . ";dbname=" . self::$dbname . ";charset=utf8mb4",
                self::$username,
                self::$password
=======
                "mysql:host=" . $host . ";dbname=" . $dbname . ";charset=utf8mb4",
                $username,
                $password
>>>>>>> origin/main
            );

            $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

            return $pdo;

        } catch (PDOException $e) {
            http_response_code(500);
            header('Content-Type: application/json');
            echo json_encode([
                'error' => 'Impossible de se connecter à la base de données.',
                'details' => $e->getMessage()
            ]);
            exit;
        }
    }
}