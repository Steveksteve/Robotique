-- Politique de conservation du démonstrateur RAA : 30 jours maximum.
-- Exécuter avec un compte MySQL autorisé sur la base raa_db.

USE raa_db;

START TRANSACTION;

DELETE FROM robot_logs
WHERE `timestamp` < NOW() - INTERVAL 30 DAY;

DELETE FROM missions
WHERE status IN ('COMPLETED', 'ERROR')
  AND updated_at < NOW() - INTERVAL 30 DAY;

COMMIT;
