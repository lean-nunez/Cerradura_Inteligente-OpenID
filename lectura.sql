-- Lecturas crudas (cada vez que el lector detecta el tag)
CREATE TABLE scans (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  tag_uid VARCHAR(100) NOT NULL,
  device_id VARCHAR(100), -- id del lector si hay varios
  rssi INT NULL,
  raw_payload TEXT NULL,
  scanned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX(tag_uid),
  INDEX(scanned_at)
);
