import mysql.connector
from mysql.connector import Error

def conectar_y_leer():
    """Conecta a la base de datos MySQL y lee los datos de las tablas."""
    
    # ⚠️ ATENCIÓN: Reemplaza estos valores con tus credenciales de MySQL Workbench/Servidor
   # Configuración de la conexión
    config = {
        'host': 'localhost',            # o la IP del servidor de MySQL
        'user': 'root',                 # tu usuario de MySQL
        'password': 'root',             # tu contraseña
        'database': 'abrir_cerradura',  # la base de datos que creaste
        'port': '3306'
}

    conexion = None
    try:
        # 1. Establecer la conexión
        print("Intentando conectar a la base de datos MySQL...")
        conexion = mysql.connector.connect(**config)

        if conexion.is_connected():
            print("✅ Conexión exitosa a la base de datos 'abrir_cerradura'.")
            
            # Crear un objeto cursor para ejecutar las consultas
            cursor = conexion.cursor()

            # --- 2. Lectura de la Tabla 'usuarios' ---
            print("\n--- Leyendo datos de la tabla 'usuarios' ---")
            
            # Consulta SQL para seleccionar todos los registros
            query_usuarios = "SELECT ID_usuarios, Nombre, Apellido, Rol, rfid_Uid FROM usuarios"
            cursor.execute(query_usuarios)
            
            # Obtener todos los resultados de la consulta
            registros_usuarios = cursor.fetchall()
            
            # Obtener los nombres de las columnas
            columnas_usuarios = [i[0] for i in cursor.description]
            print(f"Columnas: {columnas_usuarios}")
            
            # Imprimir los datos
            for fila in registros_usuarios:
                print(fila)
            
            print(f"Total de registros de usuarios: {cursor.rowcount}")

            # --- 3. Lectura de la Tabla 'registros_accesos' ---
            print("\n--- Leyendo datos de la tabla 'registros_accesos' ---")
            
            # Consulta SQL (puedes hacer un JOIN para obtener el nombre del usuario)
            query_registros = """
            SELECT 
                r.ID_registros_Acceso, 
                u.Nombre, 
                u.Apellido, 
                r.Estado, 
                r.Fecha_hora 
            FROM 
                registros_accesos r
            JOIN 
                usuarios u ON r.ID_usuarios = u.ID_usuarios
            """
            cursor.execute(query_registros)
            
            # Obtener todos los resultados
            registros_accesos = cursor.fetchall()
            
            # Obtener los nombres de las columnas
            columnas_registros = [i[0] for i in cursor.description]
            print(f"Columnas: {columnas_registros}")

            # Imprimir los datos
            for fila in registros_accesos:
                # El campo Fecha_hora será probablemente un objeto datetime, 
                # por eso lo formateamos si es necesario, aunque Python lo maneja bien.
                print(fila)
            
            print(f"Total de registros de accesos: {cursor.rowcount}")

        else:
            print("❌ No se pudo establecer la conexión.")

    except Error as e:
        # Manejo de errores de conexión o consulta
        print(f"Ocurrió un error: {e}")

    finally:
        # 4. Cerrar la conexión y el cursor
        if conexion is not None and conexion.is_connected():
            cursor.close()
            conexion.close()
            print("\nConexión a MySQL cerrada. 👋")

# Llamar a la función principal para ejecutar el script
if __name__ == "__main__":
    conectar_y_leer()