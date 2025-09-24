-- Sesiones (entrada / salida emparejadas)
CREATE TABLE sessions (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NULL,
  tag_uid VARCHAR(100) NOT NULL,
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP NULL,
  duration_seconds BIGINT NULL,
  status ENUM('OPEN','CLOSED') NOT NULL DEFAULT 'OPEN',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
  INDEX(user_id),
  INDEX(start_time),
  INDEX(end_time)
);