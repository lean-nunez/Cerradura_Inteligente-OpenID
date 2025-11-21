import mysql.connector
from mysql.connector import Error, pooling
import sys

# ============================================================
#  CONFIGURACIÓN GENERAL DE LA CONEXIÓN
# ============================================================

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "abrir_cerradura"
}

# ============================================================
#  POOL DE CONEXIONES (permite rápidas y estables)
# ============================================================

try:
    connection_pool = pooling.MySQLConnectionPool(
        pool_name="pool_cerradura",
        pool_size=5,
        pool_reset_session=True,
        **DB_CONFIG
    )
    print("[DB] ✔ Pool de conexiones inicializado correctamente.")
except Error as e:
    print(f"[DB] ❌ Error creando el pool: {e}")
    sys.exit(1)


# ============================================================
#  FUNCIÓN BASE PARA TOMAR UNA CONEXIÓN
# ============================================================

def crear_conexion():
    """Solicita una conexión desde el pool."""
    try:
        conn = connection_pool.get_connection()
        return conn
    except Error as e:
        print(f"[DB] ❌ Error obteniendo conexión del pool: {e}")
        return None


# ============================================================
#  FUNCIONES PARA TABLA USUARIOS
# ============================================================

def obtener_todos_usuarios():
    """Retorna una lista de usuarios completos."""
    conexion = crear_conexion()
    if not conexion:
        return []

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios ORDER BY ID_usuarios ASC;")
        data = cursor.fetchall()
        print(f"[DB] ✔ Usuarios obtenidos: {len(data)}")
        return data

    except Error as e:
        print(f"[USUARIOS] ❌ Error al obtener usuarios: {e}")
        return []

    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()


def agregar_usuario(nombre, apellido, rol, rfid_uid, pin_code):
    """Agrega un nuevo usuario."""
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

        print(f"[USUARIOS] ✔ Usuario agregado: {nombre} {apellido}")
        return True

    except Error as e:
        print(f"[USUARIOS] ❌ Error al agregar usuario: {e}")
        return False

    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()


def eliminar_usuario(id_usuario):
    """Elimina un usuario mediante su ID."""
    conexion = crear_conexion()
    if not conexion:
        return False

    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM usuarios WHERE ID_usuarios = %s;", (id_usuario,))
        conexion.commit()
        print(f"[USUARIOS] ✔ Usuario eliminado ID: {id_usuario}")
        return True

    except Error as e:
        print(f"[USUARIOS] ❌ Error al eliminar usuario: {e}")
        return False

    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()


# ============================================================
#  FUNCIONES PARA TABLA REGISTROS ACCESOS
# ============================================================

def obtener_registros():
    """Retorna historial de accesos con unión a usuarios."""
    conexion = crear_conexion()
    if not conexion:
        return []

    try:
        cursor = conexion.cursor(dictionary=True)
        
        # --- ¡ARREGLO APLICADO AQUÍ! ---
        # Se añade u.Rol y se renombra r.Fecha_hora para que coincida
        # con lo que pide la interfaz.
        query = """
            SELECT
                r.ID_registros_Acceso,
                r.ID_usuarios,
                u.Nombre,
                u.Rol,
                r.Estado,
                r.Fecha_hora AS Fecha_Formateada
            FROM registros_accesos r
            LEFT JOIN usuarios u
            ON u.ID_usuarios = r.ID_usuarios
            ORDER BY r.Fecha_hora DESC;
        """
        # --- FIN DEL ARREGLO ---
        
        cursor.execute(query)
        data = cursor.fetchall()
        print(f"[REGISTROS] ✔ Registros obtenidos: {len(data)}")
        return data

    except Error as e:
        print(f"[REGISTROS] ❌ Error al obtener registros: {e}")
        return []

    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()


def agregar_registro_acceso(id_usuario, estado):
    """
    Registra un evento:
    estado = 'APERTURA' o 'CIERRE'
    """
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

        print(f"[REGISTROS] ✔ Registro insertado: Usuario={id_usuario}, Estado={estado}")
        return True

    except Error as e:
        print(f"[REGISTROS] ❌ Error al insertar registro: {e}")
        return False

    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()


# ============================================================
#  FUNCIÓN EXTRA: Buscar usuario por RFID
# ============================================================

def buscar_usuario_por_rfid(uid):
    """Devuelve los datos del usuario vinculado a una tarjeta RFID."""
    conexion = crear_conexion()
    if not conexion:
        return None

    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE rfid_Uid = %s", (uid,))
        data = cursor.fetchone()

        if data:
            print(f"[RFID] ✔ Usuario encontrado: {data['Nombre']} {data['Apellido']}")
        else:
            print("[RFID] ❌ Tarjeta no registrada.")

        return data

    except Error as e:
        print(f"[RFID] ❌ Error buscando usuario: {e}")
        return None

    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()
