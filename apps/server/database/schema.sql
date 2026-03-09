CREATE DATABASE IF NOT EXISTS raa_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE raa_db;

CREATE TABLE missions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    origin VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    object VARCHAR(255) NOT NULL,
    status ENUM(
        'CREATED',
        'ASSIGNED',
        'NAVIGATING_TO_PICKUP',
        'PICKING_UP',
        'NAVIGATING_TO_DROP',
        'DROPPING_OFF',
        'COMPLETED',
        'CANCELLED',
        'FAILED',
        'EMERGENCY_STOPPED'
    ) NOT NULL DEFAULT 'CREATED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE robot_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mission_id INT NOT NULL,
    robot_x FLOAT NOT NULL,
    robot_y FLOAT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_robot_logs_mission
        FOREIGN KEY (mission_id) REFERENCES missions(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE map_points (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    label VARCHAR(150) DEFAULT NULL,
    x FLOAT NOT NULL,
    y FLOAT NOT NULL,
    description TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE INDEX idx_robot_logs_mission_id ON robot_logs(mission_id);
CREATE INDEX idx_missions_status ON missions(status);