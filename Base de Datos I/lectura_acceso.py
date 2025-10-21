import mysql.connector
from mysql.connector import Error

# ⚠️ ATENCIÓN: Reemplaza estos valores con tus credenciales
config = {
        'host': 'localhost',            # o la IP del servidor de MySQL
        'user': 'root',                 # tu usuario de MySQL
        'password': 'root',             # tu contraseña
        'database': 'abrir_cerradura',  # la base de datos que creaste
        'port': '3306'                      
}

# ----------------------------------------------------------------------
# FUNCIÓN 1: LECTURA DE DATOS (usuarios y registros_accesos)
# ----------------------------------------------------------------------

def leer_datos():
    """Conecta a la base de datos MySQL y lee los datos de las tablas."""
    conexion = None
    try:
        print("--- 1. INICIANDO LECTURA DE DATOS ---")
        conexion = mysql.connector.connect(**config)

        if conexion.is_connected():
            cursor = conexion.cursor()
            print("✅ Conexión establecida para lectura.")

            # --- Lectura de la Tabla 'usuarios' ---
            print("\n--- TABLA: usuarios ---")
            query_usuarios = "SELECT ID_usuarios, Nombre, Apellido, Rol, rfid_Uid FROM usuarios"
            cursor.execute(query_usuarios)
            
            columnas_usuarios = [i[0] for i in cursor.description]
            print(f"Columnas: {columnas_usuarios}")
            for fila in cursor.fetchall():
                print(fila)

            # --- Lectura de la Tabla 'registros_accesos' (con JOIN) ---
            print("\n--- TABLA: registros_accesos ---")
            query_registros = """
            SELECT 
                r.ID_registros_Acceso, 
                u.Nombre, 
                r.Estado, 
                r.Fecha_hora 
            FROM 
                registros_accesos r
            JOIN 
                usuarios u ON r.ID_usuarios = u.ID_usuarios
            ORDER BY r.Fecha_hora DESC
            """
            cursor.execute(query_registros)
            
            columnas_registros = [i[0] for i in cursor.description]
            print(f"Columnas: {columnas_registros}")
            for fila in cursor.fetchall():
                print(fila)
            
        else:
            print("❌ No se pudo establecer la conexión para la lectura.")

    except Error as e:
        print(f"❌ Error durante la lectura de datos: {e}")

    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()
            print("--- LECTURA FINALIZADA ---")

# ----------------------------------------------------------------------
# FUNCIÓN 2: INSERCIÓN DE DATOS (registros_accesos)
# ----------------------------------------------------------------------

def insertar_registro_acceso(id_usuario: int, estado: str):
    """Inserta un nuevo registro de acceso."""
    conexion = None
    try:
        print("\n--- 2. INICIANDO INSERCIÓN DE REGISTRO ---")
        conexion = mysql.connector.connect(**config)
        cursor = conexion.cursor()

        # Usamos %s como placeholders para prevenir Inyección SQL
        query = """
        INSERT INTO registros_accesos 
            (ID_usuarios, Estado) 
        VALUES 
            (%s, %s)
        """
        valores = (id_usuario, estado)
        
        cursor.execute(query, valores)
        
        # Guardar los cambios permanentemente en la DB
        conexion.commit()
        
        print(f"✅ Nuevo registro insertado:")
        print(f"   - Usuario ID: {id_usuario}")
        print(f"   - Estado: {estado}")
        print(f"   - ID asignado: {cursor.lastrowid}")

    except Error as e:
        if conexion and conexion.is_connected():
            # Deshacer si algo falla
            conexion.rollback() 
        print(f"❌ Error al insertar el registro: {e}")

    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()
            print("--- INSERCIÓN FINALIZADA ---")

# ----------------------------------------------------------------------
# EJECUCIÓN PRINCIPAL
# ----------------------------------------------------------------------

if __name__ == "__main__":
    
    # PASO A: Lectura inicial para ver el estado actual
    print("=============================================")
    print("ESTADO INICIAL DE LA BASE DE DATOS")
    print("=============================================")
    leer_datos()
    
    print("\n" + "="*45)
    
    # PASO B: Inserción de un nuevo registro
    # Para la prueba, usaremos el ID_usuarios = 1 (Valeria Nieves)
    print("INTENTANDO INSERTAR UN NUEVO ACCESO (ACCESO_OK)")
    insertar_registro_acceso(id_usuario=1, estado='ACCESO_OK')
    
    print("="*45 + "\n")

    # PASO C: Lectura final para confirmar la inserción
    print("=============================================")
    print("ESTADO FINAL (CONFIRMACIÓN DE INSERCIÓN)")
    print("=============================================")
    leer_datos()