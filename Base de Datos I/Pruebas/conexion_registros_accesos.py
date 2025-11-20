import mysql.connector
from datetime import datetime

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="abrir_cerradura"
    )


def registrar_acceso(id_usuario, estado):
    try:
        db = get_db_connection()
        cursor = db.cursor()

        # Guarda fecha/hora exacta con Python
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO registro_acesso (ID_usuarios, Estado, Fecha_hora)
            VALUES (%s, %s, %s)
        """, (id_usuario, estado, ahora))

        db.commit()
        cursor.close()
        db.close()
        return True

    except Exception as e:
        print("Error al registrar acceso:", e)
        return False
