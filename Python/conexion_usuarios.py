import mysql.connector
from mysql.connector import Error


# -----------------------------
# Conexión a la base de datos
# -----------------------------
def crear_conexion():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",          # poné tu pass si tenés
            database="open_id"    # asegurate que sea el nombre correcto
        )
        return conexion
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None


# -----------------------------
# OBTENER TODOS LOS USUARIOS
# -----------------------------
def obtener_todos_usuarios():
    conexion = crear_conexion()
    if not conexion:
        return []

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios")
        resultado = cursor.fetchall()
        return resultado

    except Error as e:
        print(f"Error al obtener usuarios: {e}")
        return []
    finally:
        cursor.close()
        conexion.close()


# -----------------------------
# AGREGAR USUARIO
# -----------------------------
def agregar_usuario(nombre, apellido, rol, rfid_uid, pin_code):
    conexion = crear_conexion()
    if not conexion:
        return False

    try:
        cursor = conexion.cursor()
        query = """
            INSERT INTO usuarios (Nombre, Apellido, Rol, rfid_Uid, pin_Code)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (nombre, apellido, rol, rfid_uid, pin_code))
        conexion.commit()
        return True

    except Error as e:
        print(f"Error al agregar usuario: {e}")
        return False
    finally:
        cursor.close()
        conexion.close()


# -----------------------------
# ELIMINAR USUARIO
# -----------------------------
def eliminar_usuario(id_usuario):
    conexion = crear_conexion()
    if not conexion:
        return False

    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM usuarios WHERE ID_usuarios = %s", (id_usuario,))
        conexion.commit()
        return True

    except Error as e:
        print(f"Error al eliminar usuario: {e}")
        return False
    finally:
        cursor.close()
        conexion.close()


# -----------------------------
# OBTENER REGISTROS DE ACCESOS
# -----------------------------
def obtener_registros():
    conexion = crear_conexion()
    if not conexion:
        return []

    try:
        cursor = conexion.cursor(dictionary=True)
        query = """
            SELECT
                r.ID_registros_Acceso,
                r.ID_usuarios,
                u.Nombre,
                u.Apellido,
                r.Estado,
                r.Fecha_hora
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
        cursor.close()
        conexion.close()


# -----------------------------
# AGREGAR REGISTRO DE ACCESO
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
        cursor.close()
        conexion.close()
