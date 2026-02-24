<?php

require_once __DIR__ . '/Database.php';

class MissionController
{
    public static function index()
    {
        $pdo = Database::connect();

        $stmt = $pdo->query("SELECT * FROM missions");
        $missions = $stmt->fetchAll(PDO::FETCH_ASSOC);

        echo json_encode($missions);
    }

    public static function store()
    {
        $pdo = Database::connect();

        $data = json_decode(file_get_contents("php://input"), true);

        if (!isset($data['origin']) || !isset($data['destination'])) {
            http_response_code(400);
            echo json_encode([
                'error' => 'Origin et destination sont requis.'
            ]);
            return;
        }

        $stmt = $pdo->prepare("
            INSERT INTO missions (origin, destination, status)
            VALUES (:origin, :destination, 'CREATED')
        ");

        $stmt->execute([
            'origin' => $data['origin'],
            'destination' => $data['destination']
        ]);

        echo json_encode([
            'message' => 'Mission créée avec succès.'
        ]);
    }
}
