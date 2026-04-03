<?php

require_once __DIR__ . '/Database.php';

class MissionController
{
    // GET missions
    public static function index()
    {
        header('Content-Type: application/json');
<<<<<<< HEAD

        try {
            $pdo = Database::connect();
=======

        $pdo = Database::connect();

        $stmt = $pdo->query("SELECT * FROM missions ORDER BY id DESC");
        $missions = $stmt->fetchAll(PDO::FETCH_ASSOC);
>>>>>>> origin/main

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
<<<<<<< HEAD
=======

        $pdo = Database::connect();
>>>>>>> origin/main

        try {
            $pdo = Database::connect();

<<<<<<< HEAD
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
=======
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
>>>>>>> origin/main
            ]);
        }
<<<<<<< HEAD
    }
=======

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

    public static function updateStatus($id)
    {
        header('Content-Type: application/json');

        $pdo = Database::connect();

        $data = json_decode(file_get_contents("php://input"), true);

        if (!isset($data['status'])) {
            http_response_code(400);
            echo json_encode(['error' => 'status est requis.']);
            return;
        }

        $status = trim($data['status']);

        if ($status === '') {
            http_response_code(400);
            echo json_encode(['error' => 'status ne peut pas être vide.']);
            return;
        }

        // Vérifier existence de la mission
        $stmt = $pdo->prepare("SELECT id FROM missions WHERE id = :id");
        $stmt->execute(['id' => $id]);
        $mission = $stmt->fetch(PDO::FETCH_ASSOC);

        if (!$mission) {
            http_response_code(404);
            echo json_encode(['error' => 'Mission non trouvée.']);
            return;
        }

        $stmt = $pdo->prepare("UPDATE missions SET status = :status WHERE id = :id");
        $stmt->execute(['status' => $status, 'id' => $id]);

        http_response_code(200);
        echo json_encode(['message' => 'Status mis à jour.', 'mission_id' => $id, 'status' => $status]);
    }
>>>>>>> origin/main
}