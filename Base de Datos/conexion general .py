import mysql.connector
from mysql.connector import Error
from datetime import date

# Conexión a MySQL
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="abrir_cerradura"
    )
    if conn.is_connected():
        print("Conectado a la base de datos")
except Error as e:
    print(f"Error de conexión: {e}")
    exit()

cursor = conn.cursor(dictionary=True)

# 1️⃣ Sesiones del día actual con nombre de usuario
query_today_sessions = """
SELECT s.id, u.name, s.tag_uid, s.start_time, s.end_time, s.duration_seconds
FROM sessions s
LEFT JOIN users u ON u.id = s.user_id
WHERE DATE(s.start_time) = CURDATE()
ORDER BY s.start_time;
"""
cursor.execute(query_today_sessions)
today_sessions = cursor.fetchall()
print("Sesiones de hoy:", today_sessions)

# 2️⃣ Sesiones de un usuario en un rango de fechas
user_id = 42
query_user_sessions = """
SELECT s.id, s.start_time, s.end_time, s.duration_seconds
FROM sessions s
WHERE s.user_id = %s
  AND s.start_time >= '2025-09-01'
  AND s.start_time < '2025-10-01'
ORDER BY s.start_time;
"""
cursor.execute(query_user_sessions, (user_id,))
user_sessions = cursor.fetchall()
print(f"Sesiones del usuario {user_id}:", user_sessions)

# 3️⃣ Total de horas de usuarios en un día específico
query_hours_total = """
SELECT u.id, u.name, SUM(s.duration_seconds)/3600.0 AS hours_total
FROM sessions s
JOIN users u ON u.id = s.user_id
WHERE DATE(s.start_time) = '2025-09-15'
  AND s.status = 'CLOSED'
GROUP BY u.id, u.name;
"""
cursor.execute(query_hours_total)
hours_total = cursor.fetchall()
print("Horas totales por usuario:", hours_total)

# 4️⃣ Sesiones abiertas con nombre de usuario
query_open_sessions = """
SELECT s.*, u.name
FROM sessions s
LEFT JOIN users u ON u.id = s.user_id
WHERE s.status = 'OPEN';
"""
cursor.execute(query_open_sessions)
open_sessions = cursor.fetchall()
print("Sesiones abiertas:", open_sessions)

# Cerrar cursor y conexión
cursor.close()
conn.close()
