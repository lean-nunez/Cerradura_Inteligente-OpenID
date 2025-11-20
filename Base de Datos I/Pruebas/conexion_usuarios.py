import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="abrir_cerradura"
    )

def agregar_usuario(nombre, apellido, rol, rfid_uid, pin_code):
    try:
        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO usuarios (Nombre, Apellido, Rol, rfid_Uid, pin_Code)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, apellido, rol, rfid_uid, pin_code))

        db.commit()
        cursor.close()
        db.close()
        return True

    except Exception as e:
        print("Error al agregar usuario:", e)
        return False


def existe_uid(rfid_uid):
    try:
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT ID_usuarios FROM usuarios WHERE rfid_Uid = %s", (rfid_uid,))
        data = cursor.fetchone()
        cursor.close()
        db.close()

        return data is not None

    except Exception as e:
        print("Error verificando UID:", e)
        return False
