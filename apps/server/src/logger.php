<?php

class Logger
{
    public static function logRobotEvent(
        PDO $pdo,
        int $missionId,
        float $x,
        float $y
    ): void {
        $stmt = $pdo->prepare("
            INSERT INTO robot_logs (
                mission_id,
                robot_x,
                robot_y
            )
            VALUES (?, ?, ?)
        ");

        $stmt->execute([
            $missionId,
            $x,
            $y
        ]);
    }
}