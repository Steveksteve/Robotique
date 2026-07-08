<?php

class Logger
{
    public static function logRobotEvent(
        PDO $pdo,
        ?int $missionId,
        ?string $robotId,
        ?float $x,
        ?float $y,
        ?string $status,
        ?string $message
    ): void {
        $stmt = $pdo->prepare("
            INSERT INTO robot_logs (
                mission_id,
                robot_id,
                robot_x,
                robot_y,
                status,
                message
            ) VALUES (?, ?, ?, ?, ?, ?)
        ");

        $stmt->execute([
            $missionId,
            $robotId,
            $x,
            $y,
            $status,
            $message
        ]);
    }
}
