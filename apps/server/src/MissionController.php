<?php
require_once __DIR__ . "/Logger.php";

class MissionController
{
    private $pdo;

    private $allowedStatuses = [
        "CREATED",
        "ASSIGNED",
        "NAVIGATING_TO_PICKUP",
        "PICKING_UP",
        "NAVIGATING_TO_DROP",
        "COMPLETED",
        "ERROR"
    ];

    private $allowedTransitions = [
        "CREATED" => ["ASSIGNED", "ERROR"],
        "ASSIGNED" => ["NAVIGATING_TO_PICKUP", "ERROR"],
        "NAVIGATING_TO_PICKUP" => ["PICKING_UP", "ERROR"],
        "PICKING_UP" => ["NAVIGATING_TO_DROP", "ERROR"],
        "NAVIGATING_TO_DROP" => ["COMPLETED", "ERROR"],
        "COMPLETED" => [],
        "ERROR" => []
    ];

    public function __construct($pdo)
    {
        $this->pdo = $pdo;
        header("Content-Type: application/json");
    }

    public function index()
    {
        $stmt = $this->pdo->query("SELECT * FROM missions ORDER BY id DESC");
        echo json_encode($stmt->fetchAll(PDO::FETCH_ASSOC));
    }

    public function show($id)
    {
        $stmt = $this->pdo->prepare("SELECT * FROM missions WHERE id = ?");
        $stmt->execute([$id]);

        $mission = $stmt->fetch(PDO::FETCH_ASSOC);

        if (!$mission) {
            http_response_code(404);
            echo json_encode(["error" => "Mission not found"]);
            return;
        }

        echo json_encode($mission);
    }

    public function store()
    {
        $data = json_decode(file_get_contents("php://input"), true);

        if (
            !isset($data["origin"]) ||
            !isset($data["destination"]) ||
            !isset($data["object"])
        ) {
            http_response_code(400);
            echo json_encode([
                "error" => "origin, destination and object are required"
            ]);
            return;
        }

        $stmt = $this->pdo->prepare("
            INSERT INTO missions (origin, destination, object, status)
            VALUES (?, ?, ?, 'CREATED')
        ");

        $stmt->execute([
            $data["origin"],
            $data["destination"],
            $data["object"]
        ]);

        $missionId = (int) $this->pdo->lastInsertId();

        $stmt = $this->pdo->prepare("SELECT * FROM missions WHERE id = ?");
        $stmt->execute([$missionId]);

        $mission = $stmt->fetch(PDO::FETCH_ASSOC);

        http_response_code(201);
        echo json_encode([
            "mission_id" => $missionId,
            "mission" => $mission
        ]);
    }

    public function updateStatus($id)
    {
        $data = json_decode(file_get_contents("php://input"), true);
        $newStatus = $data["status"] ?? null;

        if (!in_array($newStatus, $this->allowedStatuses, true)) {
            http_response_code(400);
            echo json_encode(["error" => "Invalid status"]);
            return;
        }

        $stmt = $this->pdo->prepare("SELECT status FROM missions WHERE id = ?");
        $stmt->execute([$id]);

        $current = $stmt->fetch(PDO::FETCH_ASSOC);

        if (!$current) {
            http_response_code(404);
            echo json_encode(["error" => "Mission not found"]);
            return;
        }

        $currentStatus = $current["status"];

        if (!in_array($newStatus, $this->allowedTransitions[$currentStatus], true)) {
            http_response_code(409);
            echo json_encode([
                "error" => "Invalid transition",
                "from" => $currentStatus,
                "to" => $newStatus
            ]);
            return;
        }

        $stmt = $this->pdo->prepare("
            UPDATE missions
            SET status = ?
            WHERE id = ?
        ");

        $stmt->execute([$newStatus, $id]);

        $robotX = isset($data["robot_x"]) ? (float) $data["robot_x"] : 0;
        $robotY = isset($data["robot_y"]) ? (float) $data["robot_y"] : 0;

        Logger::logRobotEvent(
            $this->pdo,
            (int) $id,
            $robotX,
            $robotY
        );

        $stmt = $this->pdo->prepare("SELECT * FROM missions WHERE id = ?");
        $stmt->execute([$id]);

        $mission = $stmt->fetch(PDO::FETCH_ASSOC);

        echo json_encode([
            "success" => true,
            "mission" => $mission
        ]);
    }

    public function delete($id)
    {
        $stmt = $this->pdo->prepare("SELECT id FROM missions WHERE id = ?");
        $stmt->execute([$id]);

        $mission = $stmt->fetch(PDO::FETCH_ASSOC);

        if (!$mission) {
            http_response_code(404);
            echo json_encode(["error" => "Mission not found"]);
            return;
        }

        $stmt = $this->pdo->prepare("DELETE FROM missions WHERE id = ?");
        $stmt->execute([$id]);

        echo json_encode(["success" => true]);
    }
}