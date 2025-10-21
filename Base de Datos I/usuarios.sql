create database abrir_cerradura; 

use abrir_cerradura;

-- Tabla (usuarios)

-- Tabla de usuarios
CREATE TABLE usuarios (
  ID_usuarios INT AUTO_INCREMENT PRIMARY KEY,   -- identificador único del usuario
  Nombre VARCHAR(100),
  Apellido VARCHAR(100),
  Rol VARCHAR(100),
  rfid_Uid VARCHAR(100) UNIQUE,                -- código único de la tarjeta RFID
  pin_Code INT                                 -- PIN personal del usuario
) ENGINE=InnoDB;

insert into usuarios (Nombre, Apellido, Rol, rfid_Uid, pin_Code) values
('Valeria Nieves', 'Villalba', 'Profesora', '0001', '0000');