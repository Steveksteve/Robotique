<?php

require_once __DIR__ . '/Database.php';

class MissionController
{
    public static function index()
    {
        header('Content-Type: application/json');

        $pdo = Database::connect();

        $stmt = $pdo->query("SELECT * FROM missions ORDER BY id DESC");
        $missions = $stmt->fetchAll(PDO::FETCH_ASSOC);

        echo json_encode($missions);
    }

    public static function store()
    {
        header('Content-Type: application/json');

        $pdo = Database::connect();

        $data = json_decode(file_get_contents("php://input"), true);

        if (
            !isset($data['origin']) ||
            !isset($data['destination']) ||
            !isset($data['object'])
        ) {
            http_response_code(400);
            echo json_encode([
                'error' => 'origin, destination et object sont requis.'
            ]);
            return;
        }

        $origin = trim($data['origin']);
        $destination = trim($data['destination']);
        $object = trim($data['object']);

        if ($origin === '' || $destination === '' || $object === '') {
            http_response_code(400);
            echo json_encode([
                'error' => 'origin, destination et object ne peuvent pas être vides.'
            ]);
            return;
        }

        $stmt = $pdo->prepare("
            INSERT INTO missions (origin, destination, object, status)
            VALUES (:origin, :destination, :object, :status)
        ");

        $stmt->execute([
            'origin' => $origin,
            'destination' => $destination,
            'object' => $object,
            'status' => 'CREATED'
        ]);

        http_response_code(201);
        echo json_encode([
            'message' => 'Mission créée avec succès.',
            'mission_id' => $pdo->lastInsertId()
        ]);
    }
}