import customtkinter as ctk
import serial
import mysql.connector
from datetime import datetime
from PIL import Image, ImageTk

# --- CONFIGURACIONES ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# --- CONEXIÓN SERIAL (Arduino) ---
try:
    arduino = serial.Serial('COM3', 9600)  # ⚠️ Cambiá COM3 por tu puerto real
except Exception as e:
    arduino = None
    print("⚠️ No se pudo conectar al Arduino:", e)

# --- CONEXIÓN MYSQL ---
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="abrir_cerradura"
    )
    cursor = db.cursor()
except Exception as e:
    db = None
    print("⚠️ No se pudo conectar a la base de datos:", e)

# --- FUNCIONES ---
def leer_serial():
    """Lee datos del Arduino y los muestra en pantalla + guarda en la base."""
    if arduino and arduino.in_waiting > 0:
        line = arduino.readline().decode().strip()
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_box.insert("end", f"[{ahora}]  {line}\n")
        log_box.see("end")

        # Guardar en MySQL si el mensaje es válido
        if db and line in ["ACCESO_OK", "ACCESO_DENEGADO", "RFID_INVALIDO"]:
            cursor.execute(
                "INSERT INTO registros_acceso (usuario_id, estado) VALUES (%s, %s)",
                (1, line)
            )
            db.commit()

    app.after(500, leer_serial)


def agregar_usuario():
    """Agrega un nuevo usuario a la base de datos."""
    nombre = entry_nombre.get().strip()
    rfid = entry_rfid.get().strip()
    pin = entry_pin.get().strip()

    if not nombre or not rfid or not pin:
        log_box.insert("end", "⚠️ Completá todos los campos.\n")
        return

    # Verificar si el UID ya existe
    cursor.execute("SELECT id FROM users WHERE rfid_uid = %s", (rfid,))
    if cursor.fetchone():
        log_box.insert("end", f"⚠️ El UID '{rfid}' ya está registrado.\n")
        return

    try:
        cursor.execute(
            "INSERT INTO users (name, rfid_uid, pin_code) VALUES (%s, %s, %s)",
            (nombre, rfid, pin)
        )
        db.commit()
        log_box.insert("end", f"✅ Usuario agregado: {nombre}\n")
        limpiar_campos()
    except mysql.connector.Error as e:
        log_box.insert("end", f"⚠️ Error al agregar usuario: {e}\n")


def limpiar_campos():
    entry_nombre.delete(0, "end")
    entry_rfid.delete(0, "end")
    entry_pin.delete(0, "end")


# --- FUNCIÓN FONDO ANIMADO ---
def mover_fondo():
    global fondo_x
    fondo_x -= 1  # Velocidad del movimiento
    if fondo_x <= -fondo_width:
        fondo_x = 0
    canvas_bg.coords(bg_img_id, fondo_x, 0)
    canvas_bg.coords(bg_img_id2, fondo_x + fondo_width, 0)
    app.after(30, mover_fondo)


# --- INTERFAZ ---
app = ctk.CTk()
app.title("CERRADURA INTELIGENTE - PANEL DE CONTROL")
app.geometry("700x550")

# --- FONDO ANIMADO ---
canvas_bg = ctk.CTkCanvas(app, width=700, height=550, highlightthickness=0)
canvas_bg.place(x=0, y=0)

try:
    fondo_path = r"C:\Users\ALUMNO\Downloads\Purple Pink Black Fingerprint Padlock Cyber Security Logo.png"  # Podés cambiarlo a un fondo más grande
    fondo_img = Image.open(fondo_path).resize((700, 550))
    fondo_img_tk = ImageTk.PhotoImage(fondo_img)

    fondo_width = fondo_img.width
    fondo_x = 0

    bg_img_id = canvas_bg.create_image(fondo_x, 0, anchor="nw", image=fondo_img_tk)
    bg_img_id2 = canvas_bg.create_image(fondo_x + fondo_width, 0, anchor="nw", image=fondo_img_tk)
except Exception as e:
    print("⚠️ No se pudo cargar el fondo:", e)

# --- FRAME PRINCIPAL ---
frame_main = ctk.CTkFrame(app, corner_radius=15)
frame_main.place(relx=0.5, rely=0.5, anchor="center")

# --- LOGO ---
try:
    logo_path = r"C:\Users\ALUMNO\Downloads\Purple Pink Black Fingerprint Padlock Cyber Security Logo.png"
    logo_img = ctk.CTkImage(light_image=Image.open(logo_path), size=(100, 100))
    logo_label = ctk.CTkLabel(frame_main, image=logo_img, text="")
    logo_label.pack(pady=(10, 5))
except Exception as e:
    print("⚠️ No se pudo cargar el logo:", e)

# --- TÍTULO ---
title = ctk.CTkLabel(frame_main, text="🔐 Cerradura Inteligente", font=("Arial", 22, "bold"))
title.pack(pady=5)

# --- FORMULARIO USUARIO ---
ctk.CTkLabel(frame_main, text="Nombre:").pack()
entry_nombre = ctk.CTkEntry(frame_main, width=250)
entry_nombre.pack()

ctk.CTkLabel(frame_main, text="UID RFID:").pack()
entry_rfid = ctk.CTkEntry(frame_main, width=250)
entry_rfid.pack()

ctk.CTkLabel(frame_main, text="PIN:").pack()
entry_pin = ctk.CTkEntry(frame_main, width=250, show="*")
entry_pin.pack()

btn_agregar = ctk.CTkButton(frame_main, text="Agregar Usuario", command=agregar_usuario)
btn_agregar.pack(pady=10)

# --- LOG DE EVENTOS ---
log_box = ctk.CTkTextbox(frame_main, width=600, height=200)
log_box.pack(pady=10)

# --- INICIO ---
app.after(1000, leer_serial)
app.after(30, mover_fondo)
app.mainloop()
