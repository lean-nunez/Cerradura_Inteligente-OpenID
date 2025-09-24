-- Tags RFID
CREATE TABLE rfid_tags (
  id INT AUTO_INCREMENT PRIMARY KEY,
  tag_uid VARCHAR(100) NOT NULL UNIQUE, -- el UID que devuelve el lector (ej "04A3B2C1")
  user_id INT NULL,
  description VARCHAR(200),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);