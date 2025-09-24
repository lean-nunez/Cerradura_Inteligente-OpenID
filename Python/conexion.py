import mysql.connector

def obtener_usuarios():
    """
    Conecta a la base de datos y devuelve todos los registros de la tabla 'users'.
    Retorna una lista de diccionarios.
    """
    # Configuración de la conexión
    config = {
        'user': 'root',        # ej: 'root'
        'password': 'root', # ej: '1234'
        'host': 'localhost:3306',         # o IP del servidor
        'database': 'open_id',
    }

    try:
        # Conectar a la base de datos
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)

        # Ejecutar consulta
        cursor.execute("SELECT * FROM users;")
        resultados = cursor.fetchall()

        return resultados

    except mysql.connector.Error as err:
        print("Error al conectar o consultar:", err)
        return []

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ------------------------
# Ejemplo de uso:
usuarios = obtener_usuarios()
for u in usuarios:
    print(f"ID: {u['id']}, Nombre: {u['name']}, Email: {u['email']}, Rol: {u['role']}, Activo: {u['active']}")
