-- Tabla (registros de accesos)

-- Tabla de registros de accesos
CREATE TABLE registros_accesos (
  ID_registros_Acceso INT AUTO_INCREMENT PRIMARY KEY,  -- identificador único del registro
  ID_usuarios INT,                                     -- referencia al usuario que intentó acceder
  Estado VARCHAR(50),                                  -- "ACCESO_OK", "DENEGADO"
  Fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,     -- momento del intento
  FOREIGN KEY (ID_usuarios) REFERENCES usuarios(ID_usuarios) ON DELETE CASCADE
) ENGINE=InnoDB;