<?php
require_once __DIR__ . "/Logger.php";

class MissionController
{
    private PDO $pdo;

    private array $allowedStatuses = [
        "CREATED",
        "ASSIGNED",
        "NAVIGATING_TO_PICKUP",
        "SCANNING_QR",
        "PICKING_UP",
        "NAVIGATING_TO_DROP",
        "DROPPING_OFF",
        "COMPLETED",
        "ERROR"
    ];

    private array $allowedTransitions = [
        "CREATED" => ["ASSIGNED", "ERROR"],
        "ASSIGNED" => ["NAVIGATING_TO_PICKUP", "ERROR"],
        "NAVIGATING_TO_PICKUP" => ["SCANNING_QR", "ERROR"],
        "SCANNING_QR" => ["PICKING_UP", "ERROR"],
        "PICKING_UP" => ["NAVIGATING_TO_DROP", "ERROR"],
        "NAVIGATING_TO_DROP" => ["DROPPING_OFF", "ERROR"],
        "DROPPING_OFF" => ["COMPLETED", "ERROR"],
        "COMPLETED" => [],
        "ERROR" => []
    ];

    public function __construct(PDO $pdo)
    {
        $this->pdo = $pdo;
        header("Content-Type: application/json");
    }

    private function json($payload, int $status = 200): void
    {
        http_response_code($status);
        echo json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    }

    private function body(): array
    {
        $decoded = json_decode(file_get_contents("php://input"), true);
        return is_array($decoded) ? $decoded : [];
    }

    private function nullableFloat(array $data, string $key): ?float
    {
        if (!array_key_exists($key, $data) || $data[$key] === "" || $data[$key] === null) {
            return null;
        }
        return (float) $data[$key];
    }

    private function sanitizeText(array $data, string $key, ?string $default = null): ?string
    {
        if (!array_key_exists($key, $data) || $data[$key] === null) {
            return $default;
        }
        $value = trim((string) $data[$key]);
        return $value === "" ? $default : $value;
    }

    private function findMission(int $id): ?array
    {
        $stmt = $this->pdo->prepare("SELECT * FROM missions WHERE id = ?");
        $stmt->execute([$id]);
        $mission = $stmt->fetch(PDO::FETCH_ASSOC);
        return $mission ?: null;
    }

    public function index(): void
    {
        $stmt = $this->pdo->query("SELECT * FROM missions ORDER BY id DESC");
        $this->json($stmt->fetchAll(PDO::FETCH_ASSOC));
    }

    public function show($id): void
    {
        $mission = $this->findMission((int) $id);

        if (!$mission) {
            $this->json(["error" => "Mission not found"], 404);
            return;
        }

        $this->json($mission);
    }

    public function store(): void
    {
        $data = $this->body();

        $origin = $this->sanitizeText($data, "origin");
        $destination = $this->sanitizeText($data, "destination");
        $object = $this->sanitizeText($data, "object");
        $expectedQr = $this->sanitizeText($data, "expected_qr", "a");

        if (!$origin || !$destination || !$object) {
            $this->json(["error" => "origin, destination and object are required"], 400);
            return;
        }

        $stmt = $this->pdo->prepare("
            INSERT INTO missions (
                origin, destination, object, expected_qr,
                pickup_x, pickup_y, pickup_theta,
                dropoff_x, dropoff_y, dropoff_theta,
                status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'CREATED')
        ");

        $stmt->execute([
            $origin,
            $destination,
            $object,
            $expectedQr,
            $this->nullableFloat($data, "pickup_x"),
            $this->nullableFloat($data, "pickup_y"),
            $this->nullableFloat($data, "pickup_theta"),
            $this->nullableFloat($data, "dropoff_x"),
            $this->nullableFloat($data, "dropoff_y"),
            $this->nullableFloat($data, "dropoff_theta"),
        ]);

        $missionId = (int) $this->pdo->lastInsertId();
        $mission = $this->findMission($missionId);

        $this->json(["mission_id" => $missionId, "mission" => $mission], 201);
    }

    public function updateStatus($id): void
    {
        $missionId = (int) $id;
        $data = $this->body();
        $newStatus = $data["status"] ?? null;

        if (!in_array($newStatus, $this->allowedStatuses, true)) {
            $this->json(["error" => "Invalid status", "status" => $newStatus], 400);
            return;
        }

        $mission = $this->findMission($missionId);

        if (!$mission) {
            $this->json(["error" => "Mission not found"], 404);
            return;
        }

        $currentStatus = $mission["status"];

        if ($newStatus !== $currentStatus && !in_array($newStatus, $this->allowedTransitions[$currentStatus], true)) {
            $this->json([
                "error" => "Invalid transition",
                "from" => $currentStatus,
                "to" => $newStatus
            ], 409);
            return;
        }

        $errorReason = $newStatus === "ERROR" ? ($data["error_reason"] ?? "Mission stopped") : null;

        $stmt = $this->pdo->prepare("
            UPDATE missions
            SET status = ?, error_reason = ?
            WHERE id = ?
        ");
        $stmt->execute([$newStatus, $errorReason, $missionId]);

        Logger::logRobotEvent(
            $this->pdo,
            $missionId,
            $data["robot_id"] ?? null,
            isset($data["robot_x"]) ? (float) $data["robot_x"] : null,
            isset($data["robot_y"]) ? (float) $data["robot_y"] : null,
            $newStatus,
            $errorReason
        );

        $this->json(["success" => true, "mission" => $this->findMission($missionId)]);
    }

    public function delete($id): void
    {
        $missionId = (int) $id;
        $mission = $this->findMission($missionId);

        if (!$mission) {
            $this->json(["error" => "Mission not found"], 404);
            return;
        }

        $stmt = $this->pdo->prepare("DELETE FROM missions WHERE id = ?");
        $stmt->execute([$missionId]);

        $this->json(["success" => true]);
    }

    public function logs(): void
    {
        $stmt = $this->pdo->query("
            SELECT
                rl.id,
                rl.mission_id,
                rl.robot_id,
                rl.robot_x,
                rl.robot_y,
                rl.status,
                rl.message,
                rl.timestamp,
                m.status AS mission_status
            FROM robot_logs rl
            LEFT JOIN missions m ON m.id = rl.mission_id
            ORDER BY rl.timestamp DESC
            LIMIT 200
        ");
        $this->json($stmt->fetchAll(PDO::FETCH_ASSOC));
    }

    public function mapPoints(): void
    {
        $stmt = $this->pdo->query("SELECT * FROM map_points ORDER BY name ASC");
        $this->json($stmt->fetchAll(PDO::FETCH_ASSOC));
    }
}
