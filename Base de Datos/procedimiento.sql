DELIMITER $$

CREATE PROCEDURE handle_scan(IN p_tag_uid VARCHAR(100), IN p_scanned_at TIMESTAMP)
BEGIN
  DECLARE v_user_id INT;
  DECLARE v_session_id BIGINT;

  -- Opcional: buscar usuario asociado al tag
  SELECT user_id INTO v_user_id FROM rfid_tags WHERE tag_uid = p_tag_uid LIMIT 1;

  -- Buscar si hay session abierta para ese tag (o para ese user)
  SELECT id INTO v_session_id
  FROM sessions
  WHERE tag_uid = p_tag_uid AND status = 'OPEN'
  ORDER BY start_time DESC
  LIMIT 1;

  IF v_session_id IS NOT NULL THEN
    -- Cerrar la sesión
    UPDATE sessions
    SET end_time = p_scanned_at,
        duration_seconds = TIMESTAMPDIFF(SECOND, start_time, p_scanned_at),
        status = 'CLOSED'
    WHERE id = v_session_id;
  ELSE
    -- Crear nueva sesión (entrada)
    INSERT INTO sessions (user_id, tag_uid, start_time, status)
    VALUES (v_user_id, p_tag_uid, p_scanned_at, 'OPEN');
  END IF;
END$$

DELIMITER ;

-- Trigger que llama al procedimiento después de insertar un scan
DELIMITER $$
CREATE TRIGGER trg_after_scans_insert
AFTER INSERT ON scans
FOR EACH ROW
BEGIN
  CALL handle_scan(NEW.tag_uid, NEW.scanned_at);
END$$
DELIMITER ;


SELECT s.id, u.name, s.tag_uid, s.start_time, s.end_time, s.duration_seconds
FROM sessions s
LEFT JOIN users u ON u.id = s.user_id
WHERE DATE(s.start_time) = CURDATE()
ORDER BY s.start_time;

SELECT s.id, s.start_time, s.end_time, s.duration_seconds
FROM sessions s
WHERE s.user_id = 42
  AND s.start_time >= '2025-09-01'
  AND s.start_time < '2025-10-01'
ORDER BY s.start_time;


SELECT u.id, u.name, SUM(s.duration_seconds)/3600.0 AS hours_total
FROM sessions s
JOIN users u ON u.id = s.user_id
WHERE DATE(s.start_time) = '2025-09-15'
  AND s.status = 'CLOSED'
GROUP BY u.id, u.name;

SELECT s.*, u.name
FROM sessions s
LEFT JOIN users u ON u.id = s.user_id
WHERE s.status = 'OPEN';

use open_id
