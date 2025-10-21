import mysql.connector
from datetime import date

# --- Configuración de Conexión ---
DB_CONFIG = {
    'host': 'localhost',        # o la IP del servidor de MySQL
    'user': 'root',             # tu usuario de MySQL
    'password': 'root',         # tu contraseña
    'database': 'abrir_cerradura',  # la base de datos que creaste
    'port': 3306
}


# --- FUNCIONES CRUD DE USUARIOS ---

def get_usuarios():
    """
    Lee y muestra todos los registros de la tabla 'usuarios'. (CRUD: Read)
    """
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            print("✅ Conectado exitosamente a la base de datos.")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios")
            records = cursor.fetchall()

            if records:
                print("\n--- Registros de la tabla Usuarios ---")
                for row in records:
                    print(row)
            else:
                print("\nNo se encontraron registros en la tabla Usuarios.")
    except mysql.connector.Error as err:
        print(f"❌ Error de conexión/lectura: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def insert_usuario(Nombre, Apellido, Rol, rfid_Uid, pin_Code):
    """
    Inserta un nuevo usuario en la tabla 'usuarios'. (CRUD: Create)
    """
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        sql = """
        INSERT INTO usuarios (Nombre, Apellido, Rol, rfid_Uid, pin_Code)
        VALUES (%s, %s, %s, %s, %s)
        """
        values = (Nombre, Apellido, Rol, rfid_Uid, pin_Code)

        cursor.execute(sql, values)
        conn.commit()

        print(f"✅ Usuario '{Nombre} {Apellido}' insertado correctamente.")
    except mysql.connector.Error as err:
        print(f"❌ Error al insertar el usuario: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


# --- PROGRAMA PRINCIPAL ---

if __name__ == "__main__":

    print("--- 1. Insertando usuario de prueba ---")
    insert_usuario(
        Nombre="Juan",
        Apellido="Pérez",
        Rol="Administrador",
        rfid_Uid="ABC12345",
        pin_Code="4321"
    )

    print("\n" + "="*50 + "\n")

    print("--- 2. Listando todos los usuarios ---")
    get_usuarios()
