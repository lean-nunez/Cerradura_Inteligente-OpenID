import mysql.connector
from mysql.connector import Error


# -----------------------------
# Conexión a la base de datos
# (Duplicada de conexion_usuarios.py para que el archivo sea independiente)
# -----------------------------
def crear_conexion():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",      # poné tu pass si tenés
            database="open_id"    # asegurate que sea el nombre correcto
        )
        return conexion
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None


# -----------------------------
# OBTENER REGISTROS DE ACCESOS
# -----------------------------
def obtener_registros():
    conexion = crear_conexion()
    if not conexion:
        return []

    try:
        cursor = conexion.cursor(dictionary=True)
        
        # --- CAMBIO ---
        # Modificamos la consulta para:
        # 1. Traer u.Rol
        # 2. Formatear la fecha (con DATE_FORMAT)
        # 3. Quitar campos que no usaremos (ID_registros_Acceso, Apellido, Estado)
        query = """
            SELECT
                r.ID_usuarios,
                u.Nombre,
                u.Rol,
                DATE_FORMAT(r.Fecha_hora, '%d/%m/%Y, %H:%M:%S') AS Fecha_Formateada
            FROM registros_accesos r
            LEFT JOIN usuarios u ON r.ID_usuarios = u.ID_usuarios
            ORDER BY r.Fecha_hora DESC
        """
        cursor.execute(query)
        resultado = cursor.fetchall()
        return resultado

    except Error as e:
        print(f"Error al obtener registros: {e}")
        return []
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


# -----------------------------
# AGREGAR REGISTRO DE ACCESO
# (Esta función no se usa en main_app.py pero la dejamos)
# -----------------------------
def agregar_registro_acceso(id_usuario, estado):
    conexion = crear_conexion()
    if not conexion:
        return False

    try:
        cursor = conexion.cursor()
        query = """
            INSERT INTO registros_accesos (ID_usuarios, Estado)
            VALUES (%s, %s)
        """
        cursor.execute(query, (id_usuario, estado))
        conexion.commit()
        return True

    except Error as e:
        print(f"Error al insertar registro de acceso: {e}")
        return False
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()