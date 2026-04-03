<?php

class Database
{
    private static $host = '127.0.0.1';
    private static $dbname = 'raa';
    private static $username = 'root';
    private static $password = 'TON_MOT_DE_PASSE_ICI'; // Mets ton vrai mot de passe

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
            echo json_encode([
                'error' => 'Impossible de se connecter à la base de données.',
                'details' => $e->getMessage()
            ]);
            exit;
        }
    }
}