<?php

require_once __DIR__ . '/Database.php';

class MissionController
{
    // GET missions
    public static function index()
    {
        header('Content-Type: application/json');

        try {
            $pdo = Database::connect();

            $stmt = $pdo->query("SELECT * FROM missions ORDER BY created_at DESC");
            $missions = $stmt->fetchAll(PDO::FETCH_ASSOC);

            echo json_encode([
                'success' => true,
                'message' => 'Liste des missions récupérée.',
                'data' => $missions
            ]);

        } catch (Exception $e) {
            http_response_code(500);
            echo json_encode([
                'success' => false,
                'message' => 'Erreur serveur.'
            ]);
        }
    }

    // POST missions
    public static function store()
    {
        header('Content-Type: application/json');

        try {
            $pdo = Database::connect();

            $data = json_decode(file_get_contents("php://input"), true);

            // Vérifie que le body est bien du JSON valide
            if (!is_array($data)) {
                http_response_code(400);
                echo json_encode([
                    'success' => false,
                    'message' => 'Format JSON invalide.'
                ]);
                return;
            }

            // Nettoyage des données
            $origin = isset($data['origin']) ? trim($data['origin']) : null;
            $destination = isset($data['destination']) ? trim($data['destination']) : null;

            // Validation des champs
            if (empty($origin) || empty($destination)) {
                http_response_code(400);
                echo json_encode([
                    'success' => false,
                    'message' => 'Origin et destination sont requis et ne peuvent pas être vides.'
                ]);
                return;
            }

            $stmt = $pdo->prepare("
                INSERT INTO missions (origin, destination, status)
                VALUES (:origin, :destination, 'CREATED')
            ");

            $stmt->execute([
                'origin' => $origin,
                'destination' => $destination
            ]);

            http_response_code(201);

            echo json_encode([
                'success' => true,
                'message' => 'Mission créée avec succès.'
            ]);

        } catch (Exception $e) {
            http_response_code(500);
            echo json_encode([
                'success' => false,
                'message' => 'Erreur serveur.'
            ]);
        }
    }
}