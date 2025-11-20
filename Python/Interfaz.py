import customtkinter as ctk
import serial
import mysql.connector
from datetime import datetime
from PIL import Image, ImageTk
import threading
import random
import time
import os

from conexion_usuarios import agregar_usuario, existe_uid
from conexion_registros_accesos import registrar_acceso


# ============================================================
# CONFIGURACIÓN DE LA INTERFAZ
# ============================================================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

FUENTE = ("Consolas", 13)

# ============================================================
# SERIAL ARDUINO
# ============================================================
def conectar_serial():
    puertos = ["COM3", "COM4", "COM5", "COM6"]
    for p in puertos:
        try:
            return serial.Serial(p, 9600, timeout=1)
        except:
            pass
    return None

arduino = conectar_serial()


# ============================================================
# APP PRINCIPAL
# ============================================================
app = ctk.CTk()
app.title("Cerradura Inteligente - Panel de Control")
app.geometry("1000x650")
app.resizable(False, False)

tema_actual = "dark"
modo_admin = False
animacion_activa = True

# ============================================================
# FONDO ANIMADO
# ============================================================
canvas = ctk.CTkCanvas(app, width=1000, height=650, highlightthickness=0)
canvas.place(x=0, y=0)

try:
    fondo_path = r"C:\Users\ALUMNO\Downloads\Purple Pink Black Fingerprint Padlock Cyber Security Logo.png"
    fondo_base = Image.open(fondo_path).resize((1000, 650))
    fondo_tk = ImageTk.PhotoImage(fondo_base)

    fondo_w = fondo_base.width
    fondo_x = 0

    bg1 = canvas.create_image(0, 0, anchor="nw", image=fondo_tk)
    bg2 = canvas.create_image(fondo_w, 0, anchor="nw", image=fondo_tk)
except:
    fondo_tk = None


def mover_fondo():
    global fondo_x
    if fondo_tk:
        fondo_x -= 1

        canvas.coords(bg1, fondo_x, 0)
        canvas.coords(bg2, fondo_x + fondo_w, 0)

        if fondo_x <= -fondo_w:
            fondo_x = 0

    app.after(25, mover_fondo)


# ============================================================
# TOAST (NOTIFICACIONES)
# ============================================================
def toast(msg, color="green"):
    win = ctk.CTkToplevel(app)
    win.overrideredirect(True)
    win.geometry("300x60+20+20")

    frame_t = ctk.CTkFrame(win, fg_color=color)
    frame_t.place(relwidth=1, relheight=1)

    lbl = ctk.CTkLabel(frame_t, text=msg, font=("Consolas", 14), text_color="white")
    lbl.pack(expand=True)

    def auto_close():
        time.sleep(2)
        try:
            win.destroy()
        except:
            pass

    threading.Thread(target=auto_close, daemon=True).start()


# ============================================================
# FRAME PRINCIPAL
# ============================================================
frame = ctk.CTkFrame(app, corner_radius=15, width=850, height=580)
frame.place(relx=0.5, rely=0.53, anchor="center")

# ============================================================
# LOGO
# ============================================================
try:
    logo_img = ctk.CTkImage(light_image=Image.open(fondo_path), size=(100, 100))
    lbl_logo = ctk.CTkLabel(frame, image=logo_img, text="")
    lbl_logo.pack(pady=5)
except:
    lbl_logo = ctk.CTkLabel(frame, text="🔐", font=("Consolas", 40))
    lbl_logo.pack()

# ============================================================
# TÍTULO
# ============================================================
lbl_titulo = ctk.CTkLabel(frame, text="Sistema de Acceso RFID", font=("Consolas", 24, "bold"))
lbl_titulo.pack(pady=5)

# ============================================================
# SE PARTE EN PANELES — PANEL SUPERIOR (Botones)
# ============================================================
panel_superior = ctk.CTkFrame(frame)
panel_superior.pack(pady=10)

# ---------------------------
# BOTÓN ADMIN
# ---------------------------
def abrir_login():
    login = ctk.CTkToplevel(app)
    login.title("Ingreso Admin")
    login.geometry("300x230")
    login.resizable(False, False)

    ctk.CTkLabel(login, text="Usuario:", font=FUENTE).pack(pady=5)
    user_entry = ctk.CTkEntry(login, width=220)
    user_entry.pack()

    ctk.CTkLabel(login, text="Contraseña:", font=FUENTE).pack(pady=5)
    pass_entry = ctk.CTkEntry(login, width=220, show="*")
    pass_entry.pack()

    errores = {"count": 0}

    def vibrar():
        try:
            x, y = login.winfo_x(), login.winfo_y()
            for _ in range(6):
                login.geometry(f"+{x+5}+{y}")
                login.update()
                time.sleep(0.03)
                login.geometry(f"+{x-5}+{y}")
                login.update()
                time.sleep(0.03)
            login.geometry(f"+{x}+{y}")
        except:
            pass

    def validar():
        global modo_admin

        usuario = user_entry.get()
        clave = pass_entry.get()

        if usuario == "Admin_ID" and clave == "admin123":
            modo_admin = True
            toast("Modo Admin Activado", "green")
            login.destroy()
        else:
            errores["count"] += 1
            toast("Credenciales incorrectas", "red")
            vibrar()

            if errores["count"] >= 3:
                toast("Demasiados intentos. Espere...", "red")
                login.after(3000, lambda: None)

    ctk.CTkButton(login, text="Ingresar", command=validar, width=200).pack(pady=10)


btn_admin = ctk.CTkButton(panel_superior, text="ADMIN", width=120, command=abrir_login)
btn_admin.grid(row=0, column=0, padx=10)


# ---------------------------
# BOTÓN TEMA
# ---------------------------
def cambiar_tema():
    global tema_actual
    if tema_actual == "dark":
        tema_actual = "light"
        ctk.set_appearance_mode("light")
    else:
        tema_actual = "dark"
        ctk.set_appearance_mode("dark")


btn_tema = ctk.CTkButton(panel_superior, text="Tema", width=120, command=cambiar_tema)
btn_tema.grid(row=0, column=1, padx=10)


# ============================================================
# SUBPANELES
# ============================================================
panel_tabs = ctk.CTkTabview(frame, width=820, height=420)
panel_tabs.pack()

tab_log = panel_tabs.add("Terminal Hacker")
tab_usuarios = panel_tabs.add("Usuarios")
tab_sistema = panel_tabs.add("Sistema")
tab_estadisticas = panel_tabs.add("Estadísticas")


# ============================================================
# TAB LOG — TERMINAL HACKER
# ============================================================
log_box = ctk.CTkTextbox(tab_log, width=780, height=380, font=("Consolas", 13))
log_box.pack(padx=10, pady=10)


# ============================================================
# ANIMACIÓN HACKER
# ============================================================
hacker_lines = [
    "[CORE] Iniciando seguridad de kernel...",
    "[AUTH] Checkeando la encriptacion de credenciales...",
    "[DB] leyende user de la tabla...",
    "[RFID] Esperando la Tarjeta o Tag...",
    "[SYS] Arrancando watchdog ...",
    "[NET] abriendo sistema de seguridad...",
    "[LOG] Actualizando registro temporal...",
    "[ACCESS] preparando...",
    "[AI] cargando modelo predictor...",
    "[SYS] IDLE",
    "[RFID] lector de tarjetas activo...",
    "[SYS] Heatbeat OK",
    "[WATCH] Sistema integral OK",
    "[FIREWALL] Actualizacion de reglas",
    "[SYS] Cache refrescado",
    "[SESSION] Validando token...",
    "[ENC] AES-256 Iniciado",
    "[KERNEL] sin detectar anomalias",
    "[DB] Handshake correcto",
    "[SYS] Listo..."
]

def animacion_hacker():
    while animacion_activa:
        linea = random.choice(hacker_lines)
        velocidad = random.uniform(0.003, 0.009)

        for ch in linea:
            try:
                log_box.insert("end", ch)
                log_box.update()
                time.sleep(velocidad)
            except:
                return

        log_box.insert("end", "\n")
        log_box.see("end")
        time.sleep(random.uniform(0.1, 0.7))

threading.Thread(target=animacion_hacker, daemon=True).start()


# ============================================================
# TAB USUARIOS — FORMULARIO
# ============================================================
frm_user = ctk.CTkFrame(tab_usuarios)
frm_user.pack(pady=10)

ctk.CTkLabel(frm_user, text="Nombre:", font=FUENTE).grid(row=0, column=0, padx=5, pady=5)
entry_nombre = ctk.CTkEntry(frm_user, width=200)
entry_nombre.grid(row=0, column=1)

ctk.CTkLabel(frm_user, text="Apellido:", font=FUENTE).grid(row=1, column=0, padx=5, pady=5)
entry_apellido = ctk.CTkEntry(frm_user, width=200)
entry_apellido.grid(row=1, column=1)

ctk.CTkLabel(frm_user, text="Rol:", font=FUENTE).grid(row=2, column=0, padx=5, pady=5)
entry_rol = ctk.CTkEntry(frm_user, width=200)
entry_rol.grid(row=2, column=1)

ctk.CTkLabel(frm_user, text="RFID UID:", font=FUENTE).grid(row=3, column=0, padx=5, pady=5)
entry_uid = ctk.CTkEntry(frm_user, width=200)
entry_uid.grid(row=3, column=1)

ctk.CTkLabel(frm_user, text="PIN:", font=FUENTE).grid(row=4, column=0, padx=5, pady=5)
entry_pin = ctk.CTkEntry(frm_user, width=200, show="*")
entry_pin.grid(row=4, column=1)

def click_agregar_usuario():
    if not modo_admin:
        toast("Solo admin puede agregar usuarios", "red")
        return

    nombre = entry_nombre.get().strip()
    apellido = entry_apellido.get().strip()
    rol = entry_rol.get().strip()
    uid = entry_uid.get().strip()
    pin = entry_pin.get().strip()

    if not (nombre and apellido and rol and uid and pin):
        toast("Completa todos los campos", "red")
        return

    if existe_uid(uid):
        toast("UID ya registrado", "red")
        return

    if agregar_usuario(nombre, apellido, rol, uid, pin):
        toast("Usuario agregado", "green")
    else:
        toast("Error al agregar usuario", "red")

btn_add_user = ctk.CTkButton(tab_usuarios, text="AGREGAR USUARIO", command=click_agregar_usuario)
btn_add_user.pack(pady=10)

# ============================================================
# TAB USUARIOS — LISTA DE USUARIOS (CONSULTA)
# ============================================================
lista_usuarios_box = ctk.CTkTextbox(tab_usuarios, width=780, height=200, font=("Consolas", 12))
lista_usuarios_box.pack(pady=10)

def cargar_usuarios():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="abrir_cerradura"
        )
        cursor = db.cursor()
        cursor.execute("SELECT ID_usuarios, Nombre, Apellido, Rol, rfid_Uid FROM usuarios")
        data = cursor.fetchall()

        lista_usuarios_box.delete("1.0", "end")
        lista_usuarios_box.insert("end", "ID | Nombre | Apellido | Rol | RFID\n")
        lista_usuarios_box.insert("end", "-"*80 + "\n")

        for user in data:
            linea = f"{user[0]} | {user[1]} | {user[2]} | {user[3]} | {user[4]}\n"
            lista_usuarios_box.insert("end", linea)

        lista_usuarios_box.see("end")
        cursor.close()
        db.close()
    except:
        lista_usuarios_box.insert("end", "⚠ Error cargando usuarios.\n")

btn_refrescar_users = ctk.CTkButton(tab_usuarios, text="REFRESCAR LISTA", command=cargar_usuarios)
btn_refrescar_users.pack(pady=5)


# ============================================================
# TAB SISTEMA — ESTADOS
# ============================================================
frame_sys = ctk.CTkFrame(tab_sistema)
frame_sys.pack(pady=10)

lbl_estado_serial = ctk.CTkLabel(frame_sys, text="Serial:", font=FUENTE)
lbl_estado_serial.grid(row=0, column=0, padx=10, pady=5)
lbl_serial_val = ctk.CTkLabel(frame_sys, text="Desconectado", text_color="red", font=FUENTE)
lbl_serial_val.grid(row=0, column=1, padx=10, pady=5)

lbl_estado_db = ctk.CTkLabel(frame_sys, text="Base de Datos:", font=FUENTE)
lbl_estado_db.grid(row=1, column=0, padx=10, pady=5)
lbl_db_val = ctk.CTkLabel(frame_sys, text="Desconectado", text_color="red", font=FUENTE)
lbl_db_val.grid(row=1, column=1, padx=10, pady=5)

lbl_watchdog = ctk.CTkLabel(frame_sys, text="Watchdog:", font=FUENTE)
lbl_watchdog.grid(row=2, column=0, padx=10, pady=5)
lbl_watchdog_val = ctk.CTkLabel(frame_sys, text="Activo", text_color="green", font=FUENTE)
lbl_watchdog_val.grid(row=2, column=1, padx=10, pady=5)


def verificar_serial():
    if arduino and arduino.is_open:
        lbl_serial_val.configure(text="Conectado", text_color="green")
    else:
        lbl_serial_val.configure(text="Desconectado", text_color="red")

    app.after(1000, verificar_serial)


def verificar_db():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="abrir_cerradura"
        )
        db.close()
        lbl_db_val.configure(text="Conectada", text_color="green")
    except:
        lbl_db_val.configure(text="Desconectada", text_color="red")

    app.after(2000, verificar_db)


# ============================================================
# TAB ESTADÍSTICAS — ACCESOS
# ============================================================
frame_stats = ctk.CTkFrame(tab_estadisticas)
frame_stats.pack(pady=10)

txt_stats = ctk.CTkTextbox(tab_estadisticas, width=780, height=350, font=("Consolas", 12))
txt_stats.pack(pady=10)

def cargar_estadisticas():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="abrir_cerradura"
        )
        cursor = db.cursor()
        cursor.execute("SELECT Estado, COUNT(*) FROM registro_acesso GROUP BY Estado")
        data = cursor.fetchall()

        ok = 0
        den = 0

        for estado, cant in data:
            if estado == "ACCESO_OK":
                ok = cant
            elif estado == "ACCESO_DENEGADO":
                den = cant

        txt_stats.delete("1.0", "end")
        txt_stats.insert("end", "📊 Estadísticas del Sistema\n")
        txt_stats.insert("end", "-"*60 + "\n\n")

        txt_stats.insert("end", f"Accesos permitidos: {ok}\n")
        txt_stats.insert("end", f"Accesos denegados: {den}\n\n")

        max_v = max(ok, den, 1)

        txt_stats.insert("end", "Gráfico:\n")
        txt_stats.insert("end", f"OK   | {'█' * int((ok/max_v)*40)} {ok}\n")
        txt_stats.insert("end", f"DEN  | {'█' * int((den/max_v)*40)} {den}\n")

        cursor.close()
        db.close()

    except:
        txt_stats.insert("end", "⚠ Error al cargar estadísticas.\n")


btn_stats = ctk.CTkButton(tab_estadisticas, text="ACTUALIZAR", command=cargar_estadisticas)
btn_stats.place(x=350, y=10)


# ============================================================
# LECTURA SERIAL — ARDUINO
# ============================================================
def leer_serial():
    if arduino and arduino.in_waiting > 0:
        try:
            msg = arduino.readline().decode(errors="ignore").strip()
        except:
            msg = ""

        if msg:
            ahora = datetime.now().strftime("%H:%M:%S")
            log_box.insert("end", f"[ARDUINO {ahora}] {msg}\n")
            log_box.see("end")

            if msg in ["ACCESO_OK", "ACCESO_DENEGADO"]:
                registrar_acceso(1, msg)

    app.after(300, leer_serial)


# ============================================================
# PING SERIAL
# ============================================================
def ping_serial():
    if arduino and arduino.is_open:
        try:
            arduino.write(b"PING\n")
        except:
            pass
    app.after(5000, ping_serial)


# ============================================================
# LIMPIAR LOG
# ============================================================
def limpiar_log():
    log_box.delete("1.0", "end")

btn_limpiar_log = ctk.CTkButton(tab_log, text="LIMPIAR LOG", command=limpiar_log)
btn_limpiar_log.pack(pady=5)


# ============================================================
# INICIO DE TAREAS
# ============================================================
mover_fondo()
verificar_serial()
verificar_db()
leer_serial()
ping_serial()

# ============================================================
# LOOP PRINCIPAL
# ============================================================
app.mainloop()

