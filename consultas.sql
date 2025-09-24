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
