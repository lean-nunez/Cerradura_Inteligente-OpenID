-- Tabla usuarios
CREATE TABLE IF NOT EXISTS usuarios (
  ID_usuarios INT AUTO_INCREMENT PRIMARY KEY,
  Nombre VARCHAR(100),
  Apellido VARCHAR(100),
  Rol VARCHAR(100),
  rfid_Uid VARCHAR(100) UNIQUE,
  pin_Code INT
) ENGINE=InnoDB;


-- Usuario administrador
INSERT INTO usuarios (Nombre, Apellido, Rol, rfid_Uid, pin_Code)
VALUES ('Admin', 'System', 'Administrador', 'ADMIN-ID', 9999);

-- Usuario Leandro Nuñez
INSERT INTO usuarios (Nombre, Apellido, Rol, rfid_Uid, pin_Code)
VALUES ('Leandro', 'Nuñez', 'Usuario', '4A 87 F9 04', 4321);