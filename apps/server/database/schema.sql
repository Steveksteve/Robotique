CREATE DATABASE IF NOT EXISTS raa_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE raa_db;

DROP TABLE IF EXISTS robot_logs;
DROP TABLE IF EXISTS map_points;
DROP TABLE IF EXISTS missions;

CREATE TABLE missions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    origin VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    object VARCHAR(255) NOT NULL,
    expected_qr VARCHAR(255) DEFAULT 'a',
    pickup_x FLOAT DEFAULT NULL,
    pickup_y FLOAT DEFAULT NULL,
    pickup_theta FLOAT DEFAULT NULL,
    dropoff_x FLOAT DEFAULT NULL,
    dropoff_y FLOAT DEFAULT NULL,
    dropoff_theta FLOAT DEFAULT NULL,
    status ENUM(
        'CREATED',
        'ASSIGNED',
        'NAVIGATING_TO_PICKUP',
        'SCANNING_QR',
        'PICKING_UP',
        'NAVIGATING_TO_DROP',
        'DROPPING_OFF',
        'COMPLETED',
        'ERROR'
    ) DEFAULT 'CREATED',
    error_reason TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE robot_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mission_id INT DEFAULT NULL,
    robot_id VARCHAR(100) DEFAULT NULL,
    robot_x FLOAT DEFAULT NULL,
    robot_y FLOAT DEFAULT NULL,
    status VARCHAR(64) DEFAULT NULL,
    message VARCHAR(255) DEFAULT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_robot_logs_mission
        FOREIGN KEY (mission_id) REFERENCES missions(id)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE map_points (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    label VARCHAR(150) DEFAULT NULL,
    x FLOAT NOT NULL,
    y FLOAT NOT NULL,
    theta FLOAT DEFAULT 0,
    description TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_robot_logs_mission_id ON robot_logs(mission_id);
CREATE INDEX idx_robot_logs_robot_id ON robot_logs(robot_id);
CREATE INDEX idx_missions_status ON missions(status);

INSERT INTO map_points (name, label, x, y, theta, description) VALUES
('pickup_default', 'Point A - scan QR / prise objet', 2.62, 6.12, -1.90, 'Point de récupération par défaut'),
('dropoff_default', 'Point B - dépôt objet', 1.32, 2.18, -1.90, 'Point de dépôt par défaut');
