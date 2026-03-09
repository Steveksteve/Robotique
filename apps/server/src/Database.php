<?php

class Database
{
    private static $host = 'localhost';
    private static $dbname = 'raa_db';
    private static $username = 'root';
    private static $password = '';

    public static function connect()
    {
        try {
            $pdo = new PDO(
                "mysql:host=" . self::$host . ";dbname=" . self::$dbname . ";charset=utf8mb4",
                self::$username,
                self::$password
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