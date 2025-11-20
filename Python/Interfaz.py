import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk  # <--- Importado para el logo
from conexion_usuarios import (
    obtener_todos_usuarios,
    agregar_usuario,
    eliminar_usuario,
    # Se quita obtener_registros de aquí
)
from Conexion_registro_accesos import (
    obtener_registros,
)

ADMIN_USER = "Admin"
ADMIN_PASS = "Admin-id"


# =======================
#         LOGIN
# =======================

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Login del Sistema")
        self.geometry("400x320")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        frame = ctk.CTkFrame(self)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        title = ctk.CTkLabel(frame, text="Iniciar Sesión", font=("Segoe UI", 28, "bold"))
        title.pack(pady=10)

        self.user_entry = ctk.CTkEntry(frame, placeholder_text="Usuario")
        self.user_entry.pack(pady=10, fill="x", padx=20)

        self.pass_entry = ctk.CTkEntry(frame, placeholder_text="Contraseña", show="*")
        self.pass_entry.pack(pady=10, fill="x", padx=20)

        login_btn = ctk.CTkButton(frame, text="Ingresar", command=self.check_login)
        login_btn.pack(pady=15)

        self.mode_switch = ctk.CTkSwitch(
            frame,
            text="Modo claro / oscuro",
            command=self.change_mode
        )
        self.mode_switch.pack(pady=10)
        
        # Centrar ventana al iniciar
        self.after(100, self.center_window)

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def change_mode(self):
        mode = "light" if ctk.get_appearance_mode() == "Dark" else "dark"
        ctk.set_appearance_mode(mode)

    def check_login(self):
        user = self.user_entry.get()
        pw = self.pass_entry.get()

        # --- FIX: GESTIÓN DE VENTANAS ---
        # No destruimos la ventana de login, solo la ocultamos.
        # Las otras ventanas se abren como Toplevel (ventanas secundarias).
        
        self.withdraw()  # Ocultar ventana de login
        
        if user == ADMIN_USER and pw == ADMIN_PASS:
            try:
                admin_win = AdminWindow(self)
                admin_win.grab_set()  # Hacer modal
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir la ventana de admin: {e}")
                self.deiconify() # Mostrar login de nuevo si falla
        else:
            # Lógica original: cualquier otro login abre la vista de usuario
            try:
                user_win = UserWindow(self)
                user_win.grab_set() # Hacer modal
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir la ventana de usuario: {e}")
                self.deiconify() # Mostrar login de nuevo si falla


# =======================
#    PANEL ADMIN
# =======================

class AdminWindow(ctk.CTkToplevel): # <-- FIX: Cambiado a CTkToplevel
    
    # Acepta 'master' (la ventana de login) como argumento
    def __init__(self, master):
        super().__init__(master)
        self.master = master # Guardar referencia a la ventana principal (Login)

        self.title("Panel Administrador")
        self.geometry("800x650") # <-- Aumenté un poco el alto para el nuevo form

        # FIX: Manejar el cierre de esta ventana
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Tabs
        self.tab = ctk.CTkTabview(self, width=760, height=610)
        self.tab.pack(padx=20, pady=20)

        # pestañas
        self.users_tab = self.tab.add("Usuarios")
        self.log_tab = self.tab.add("Registros")

        self.build_users_tab()
        self.build_logs_tab()

    def on_close(self):
        """Se ejecuta cuando se cierra la ventana de Admin."""
        self.master.deiconify()  # <-- Vuelve a mostrar la ventana de login
        self.destroy()           # <-- Destruye esta ventana Toplevel

    def build_users_tab(self):
        # --- Tabla (Scrollable Frame) ---
        # Le damos un alto fijo para que el formulario quepa debajo
        self.users_table = ctk.CTkScrollableFrame(self.users_tab, width=720, height=250)
        self.users_table.pack(pady=10, fill="x", expand=False)

        self.refresh_users_table()

        # --- Formulario (con el nuevo estilo) ---
        form_frame = ctk.CTkFrame(self.users_tab, corner_radius=15)
        form_frame.pack(pady=10, padx=10, fill="x")

        # --- Logo (Opcional: descomenta si tienes la imagen) ---
        # try:
        #     # Esta es la ruta de tu segundo script
        #     logo_path = r"C:\Users\ALUMNO\Downloads\Purple Pink Black Fingerprint Padlock Cyber Security Logo.png"
        #     logo_img_data = Image.open(logo_path)
        #     logo_img = ctk.CTkImage(light_image=logo_img_data, size=(80, 80))
        #     logo_label = ctk.CTkLabel(form_frame, image=logo_img, text="")
        #     logo_label.pack(pady=(10, 0))
        # except Exception as e:
        #     print(f"No se pudo cargar el logo: {e}. Se omite.")

        form_title = ctk.CTkLabel(form_frame, text="🔐 Agregar Nuevo Usuario", font=("Segoe UI", 20, "bold"))
        form_title.pack(pady=(10, 15))

        # Usar un grid para alinear labels y entries
        grid_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        grid_frame.pack(pady=10, padx=20)

        # --- Campos ---
        ctk.CTkLabel(grid_frame, text="Nombre:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.in_nombre = ctk.CTkEntry(grid_frame, placeholder_text="Nombre", width=250)
        self.in_nombre.grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(grid_frame, text="Apellido:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.in_apellido = ctk.CTkEntry(grid_frame, placeholder_text="Apellido", width=250)
        self.in_apellido.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(grid_frame, text="Rol:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.in_rol = ctk.CTkEntry(grid_frame, placeholder_text="Rol (e.g., 'Empleado')", width=250)
        self.in_rol.grid(row=2, column=1, padx=5, pady=5)

        ctk.CTkLabel(grid_frame, text="UID RFID:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.in_uid = ctk.CTkEntry(grid_frame, placeholder_text="UID de la tarjeta/llavero", width=250)
        self.in_uid.grid(row=3, column=1, padx=5, pady=5)

        ctk.CTkLabel(grid_frame, text="PIN:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.in_pin = ctk.CTkEntry(grid_frame, placeholder_text="PIN numérico", width=250, show="*")
        self.in_pin.grid(row=4, column=1, padx=5, pady=5)

        # --- Botón ---
        add_btn = ctk.CTkButton(form_frame, text="Agregar Usuario", command=self.add_user)
        add_btn.pack(pady=(10, 20))


    def refresh_users_table(self):
        for w in self.users_table.winfo_children():
            w.destroy()

        try:
            users = obtener_todos_usuarios()
        except Exception as e:
            ctk.CTkLabel(self.users_table, text=f"Error al cargar usuarios: {e}", text_color="red").pack()
            return

        # Encabezados
        headers = ["ID", "Nombre", "Apellido", "Rol", "UID", "Acción"]
        header_row = ctk.CTkFrame(self.users_table)
        header_row.pack(fill="x", padx=5)

        widths = [50, 120, 120, 100, 150, 80] # Anchos de columna
        for col, h in enumerate(headers):
            ctk.CTkLabel(header_row, text=h, width=widths[col], font=("Segoe UI", 12, "bold")).grid(row=0, column=col, sticky="w")
        
        self.users_table.grid_columnconfigure(0, weight=0)

        # Filas
        for u in users: # <-- 'u' AHORA ES UN DICCIONARIO
            row_frame = ctk.CTkFrame(self.users_table)
            row_frame.pack(fill="x", pady=2, padx=5)

            # --- CAMBIO ---
            # Extraemos los datos del diccionario 'u'
            # Los nombres (ej: 'ID_usuarios') deben coincidir con los de tu BBDD
            user_id = u.get('ID_usuarios', 'N/A')
            nombre = u.get('Nombre', 'N/A')
            apellido = u.get('Apellido', 'N/A')
            rol = u.get('Rol', 'N/A')
            uid_rfid = u.get('rfid_Uid', 'N/A') # Nombre de columna de tu BBDD

            datos_fila = [user_id, nombre, apellido, rol, uid_rfid]

            # Llenamos la fila
            for col, val in enumerate(datos_fila): 
                ctk.CTkLabel(row_frame, text=str(val), width=widths[col], anchor="w").grid(row=0, column=col, sticky="w")

            del_btn = ctk.CTkButton(
                row_frame, text="Eliminar",
                width=widths[5],
                fg_color="#D00000", hover_color="#800000",
                # --- CAMBIO ---
                # Pasamos el 'user_id' correcto a la función lambda
                command=lambda current_id=user_id: self.delete_user(current_id)
            )
            del_btn.grid(row=0, column=5, padx=5)

    def add_user(self):
        nombre = self.in_nombre.get()
        apellido = self.in_apellido.get()
        rol = self.in_rol.get()
        uid = self.in_uid.get()
        pin = self.in_pin.get()
        
        if not all([nombre, apellido, rol, uid, pin]):
            messagebox.showwarning("Campos incompletos", "Por favor, complete todos los campos.")
            return
            
        try:
            # Los nombres de los parámetros (uid, pin) coinciden con los de agregar_usuario
            agregar_usuario(nombre, apellido, rol, uid, pin) 
            messagebox.showinfo("Éxito", "Usuario agregado correctamente.")
            self.refresh_users_table()
            # Limpiar campos
            self.in_nombre.delete(0, "end")
            self.in_apellido.delete(0, "end")
            self.in_rol.delete(0, "end")
            self.in_uid.delete(0, "end")
            self.in_pin.delete(0, "end")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar el usuario: {e}")

    def delete_user(self, user_id):
        if messagebox.askyesno("Confirmar", f"¿Está seguro que desea eliminar al usuario ID: {user_id}?"):
            try:
                eliminar_usuario(user_id)
                messagebox.showinfo("Éxito", "Usuario eliminado.")
                self.refresh_users_table()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el usuario: {e}")

    # -------------------- REGISTROS --------------------

    def build_logs_tab(self):
        self.logs_table = ctk.CTkScrollableFrame(self.log_tab, width=720, height=520)
        self.logs_table.pack(pady=10)
        self.refresh_logs()

    def refresh_logs(self):
        for w in self.logs_table.winfo_children():
            w.destroy()

        try:
            logs = obtener_registros()
        except Exception as e:
            ctk.CTkLabel(self.logs_table, text=f"Error al cargar registros: {e}", text_color="red").pack()
            return

        # --- CAMBIO ---
        # Headers actualizados a los 4 campos que pediste
        headers = ["ID Usuario", "Nombre", "Rol", "Fecha y Hora"]
        header_row = ctk.CTkFrame(self.logs_table)
        header_row.pack(fill="x", padx=5)

        # --- CAMBIO ---
        # Ajustamos los anchos para 4 columnas
        widths = [100, 160, 160, 190] # Anchos ajustados
        for col, h in enumerate(headers):
            ctk.CTkLabel(header_row, text=h, width=widths[col], font=("Segoe UI", 12, "bold"), anchor="w").grid(row=0, column=col)

        for r in logs: # <-- 'r' AHORA ES UN DICCIONARIO
            row = ctk.CTkFrame(self.logs_table)
            row.pack(fill="x", pady=2, padx=5)

            # --- CAMBIO ---
            # Extraemos solo los datos que pediste
            user_id = r.get('ID_usuarios', 'N/A')
            nombre = r.get('Nombre', '---')
            rol = r.get('Rol', '---') # <-- Nuevo campo
            fecha = r.get('Fecha_Formateada', 'N/A') # <-- Nuevo campo (ya formateado)
            
            # Asegurarse que la fecha sea un string para mostrarla
            if not isinstance(fecha, str):
                fecha = str(fecha)

            # --- CAMBIO ---
            # Agregamos los 4 campos a la fila
            datos_fila = [user_id, nombre, rol, fecha]

            for col, val in enumerate(datos_fila):
                ctk.CTkLabel(row, text=str(val), width=widths[col], anchor="w").grid(row=0, column=col)


# =======================
# PANEL USUARIO
# =======================

class UserWindow(ctk.CTkToplevel): # <-- FIX: Cambiado a CTkToplevel
    
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.title("Registros de Acceso")
        self.geometry("700x450")
        
        # FIX: Manejar el cierre de esta ventana
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        frame = ctk.CTkFrame(self)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.table = ctk.CTkScrollableFrame(frame)
        self.table.pack(fill="both", expand=True)

        self.load_data()

    def on_close(self):
        """Se ejecuta cuando se cierra la ventana de Usuario."""
        self.master.deiconify() # <-- Vuelve a mostrar la ventana de login
        self.destroy()          # <-- Destruye esta ventana Toplevel

    def load_data(self):
        for w in self.table.winfo_children():
            w.destroy()

        try:
            registros = obtener_registros()
        except Exception as e:
            ctk.CTkLabel(self.table, text=f"Error al cargar registros: {e}", text_color="red").pack()
            return
            
        # --- CAMBIO ---
        # Actualizamos la vista de Usuario para que sea igual a la del Admin
        headers = ["ID Usuario", "Nombre", "Rol", "Fecha y Hora"]
        header = ctk.CTkFrame(self.table)
        header.pack(fill="x", padx=5)
        
        # --- CAMBIO ---
        widths = [100, 160, 160, 190] # Anchos ajustados
        for col, h in enumerate(headers):
            ctk.CTkLabel(header, text=h, width=widths[col], font=("Segoe UI", 12, "bold"), anchor="w").grid(row=0, column=col)

        for r in registros: # <-- 'r' AHORA ES UN DICCIONARIO
            row = ctk.CTkFrame(self.table)
            row.pack(fill="x", pady=2, padx=5)

            # --- CAMBIO ---
            # Extraemos solo los datos que pediste
            user_id = r.get('ID_usuarios', 'N/A')
            nombre = r.get('Nombre', '---')
            rol = r.get('Rol', '---') # <-- Nuevo campo
            fecha = r.get('Fecha_Formateada', 'N/A') # <-- Nuevo campo (ya formateado)
            
            if not isinstance(fecha, str):
                fecha = str(fecha)

            # --- CAMBIO ---
            datos_fila = [user_id, nombre, rol, fecha]

            for col, val in enumerate(datos_fila):
                ctk.CTkLabel(row, text=str(val), width=widths[col], anchor="w").grid(row=0, column=col)


# =======================
#         MAIN
# =======================

if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop() # <-- FIX: Solo se llama a mainloop UNA VEZ