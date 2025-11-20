-- Tabla registros de accesos
CREATE TABLE IF NOT EXISTS registros_accesos (
  ID_registros_Acceso INT AUTO_INCREMENT PRIMARY KEY,
  ID_usuarios INT,
  Estado VARCHAR(50),
  Fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (ID_usuarios) REFERENCES usuarios(ID_usuarios) ON DELETE CASCADE
) ENGINE=InnoDB;
