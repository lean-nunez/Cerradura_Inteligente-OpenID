import serial
import mysql.connector

# Conexión a Arduino
ser = serial.Serial('COM3', 9600)  # Cambiar COM por tu puerto

# Conexión a MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="abrir_cerradura"
)
cursor = db.cursor()

while True:
    linea = ser.readline().decode().strip()
    if linea:
        parts = linea.split(',')
        ID_usuario = parts[0] if parts[0] != '0' else None
        estado = parts[1]
        fecha_hora = parts[2]

        sql = "INSERT INTO registros_accesos (ID_usuarios, Estado, Fecha_hora) VALUES (%s, %s, %s)"
        cursor.execute(sql, (ID_usuario, estado, fecha_hora))
        db.commit()
        print("Registro insertado:", ID_usuario, estado, fecha_hora)
