# 🔐 **OpenID – Sistema de Cerradura Inteligente**

## 📘 Descripción del Proyecto
**OpenID** es un sistema de cerradura inteligente desarrollado como proyecto final de **5.º año**, orientado a la **automatización, programación y ciberseguridad**.  
El proyecto integra hardware y software para ofrecer un mecanismo de acceso **seguro, confiable y escalable**, utilizando tecnologías **RFID/NFC**, bases de datos y una aplicación de escritorio.

---

## ⚙️ Características Principales
- 🪪 **Autenticación RFID/NFC:** Acceso mediante tarjetas o tags registrados.  
- 🔐 **Control de privilegios:**  
  - **Administrador:** Puede **agregar usuarios, eliminarlos y consultar todos los registros de acceso**.  
  - **Usuario estándar:** Solo puede **visualizar los accesos asociados a la cerradura**, sin permisos de gestión.  
- 📂 **Registro de accesos:** Cada evento es almacenado en **MySQL**, permitiendo trazabilidad y auditoría completa.  
- 🔌 **Interacción con Arduino:** Comunicación serial con **Arduino UNO**, que controla el mecanismo físico de la cerradura.  
- 🚨 **Sistema de alarma:** Se activa tras múltiples intentos fallidos de autenticación.

---

## 🧰 Tecnologías Utilizadas
| 🧩 Categoría | 🛠️ Herramientas |
|--------------|------------------|
| Hardware | Arduino UNO |
| Lector | Módulo RFID RC522 |
| Base de Datos | MySQL |
| Lenguaje | Python |
| Librerías | `customtkinter` |
| Interfaz | GUI en modo oscuro |
| Control de versiones | GitHub |

---

## 🎯 Objetivos Técnicos
- Integrar conocimientos de **electrónica, programación y redes**.  
- Desarrollar un sistema funcional combinando **hardware + software + base de datos**.  
- Implementar buenas prácticas de documentación, arquitectura y seguridad.  
- Preparar el sistema para futuras ampliaciones como **aplicaciones móviles e IoT**.

---

## 🧩 Diseño del Sistema
El diseño del circuito y el prototipo pueden visualizarse en el siguiente enlace:  
👉 **Circuito en Drive** *(enlace proporcionado por el autor)*

---

## 👥 Equipo de Desarrollo
- Leandro Nuñez  
- Santiago Vigna  
- Machado  
- Gómez  

---

## 🚀 Estado Actual del Proyecto
📌 **Versión:** v1.0 (en desarrollo)

### 🔧 Próximas Mejoras
- Mejora del diseño visual de la interfaz.  
- Implementación de cifrado en la base de datos.  
- Pruebas de seguridad y rendimiento.  
- Bot de notificaciones sobre aperturas, bloqueos e intentos fallidos.

---

## 📜 Licencia
Proyecto desarrollado con fines **educativos y experimentales**.  
Todos los derechos reservados © 2025 — *Equipo OpenID.*
