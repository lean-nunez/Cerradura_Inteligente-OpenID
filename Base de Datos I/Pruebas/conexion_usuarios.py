import mysql.connector

# Configuración de la conexión
config = {
    'host': 'localhost',        # o la IP del servidor de MySQL
    'user': 'root',             # tu usuario de MySQL
    'password': 'root',         # tu contraseña
    'database': 'abrir_cerradura'  # la base de datos que creaste
}

try:
    # Crear la conexión
    conexion = mysql.connector.connect(**config)

    if conexion.is_connected():
        print("¡Conexión exitosa a la base de datos!")

        # Crear un cursor para ejecutar consultas
        cursor = conexion.cursor()

        # Verificar las tablas existentes
        cursor.execute("SHOW TABLES")
        tablas = cursor.fetchall()
        print("Tablas en la base de datos:")
        for tabla in tablas:
            print(tabla[0])

except mysql.connector.Error as e:
    print("Error al conectar a MySQL:", e)

finally:
    if 'conexion' in locals() and conexion.is_connected():
        cursor.close()
        conexion.close()
        print("Conexión cerrada.")