
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
from PIL import Image, ImageTk  # pip install Pillow
import os
import sys

# Variables globales para usuario, IP, socket, hilos e íconos
username = None
server_ip = None
sock = None
thread = None
own_icon_photo = None
other_icon_photo = None

def show_login(root):
    """Crea una ventana Toplevel para ingresar nombre de usuario e IP. Retorna al cerrar."""
    login = tk.Toplevel(root)
    login.title("Iniciar Sesión")
    login.geometry("300x180")
    login.resizable(False, False)

    tk.Label(login, text="Nombre de usuario:", font=("Helvetica", 12)).pack(pady=(10, 2))
    username_entry = tk.Entry(login, font=("Helvetica", 12))
    username_entry.pack(pady=5, padx=10, fill=tk.X)

    tk.Label(login, text="IP del servidor:", font=("Helvetica", 12)).pack(pady=(10, 2))
    ip_entry = tk.Entry(login, font=("Helvetica", 12))
    ip_entry.pack(pady=5, padx=10, fill=tk.X)

    def on_submit():
        if username_entry.get().strip() == "" or ip_entry.get().strip() == "":
            messagebox.showerror("Error", "Ambos campos son requeridos.")
        else:
            global username, server_ip
            username = username_entry.get().strip()
            server_ip = ip_entry.get().strip()
            login.destroy()

    tk.Button(login, text="Conectar", command=on_submit, font=("Helvetica", 12),
              bg="#4CAF50", fg="white").pack(pady=10)

    login.grab_set()
    root.wait_window(login)

def build_chat_ui(root):
    """Construye la interfaz de chat una vez obtenidos username e IP."""
    root.title("Chat App - Mejorado")
    root.geometry("500x600")
    root.configure(bg="#f0f0f0")

    # -------------------------
    # Encabezado (sin ícono)
    # -------------------------
    header_frame = tk.Frame(root, bg="#3b5998", height=60)
    header_frame.pack(side=tk.TOP, fill=tk.X)
    title_label = tk.Label(header_frame, text="Chat App", bg="#3b5998",
                           fg="white", font=("Helvetica", 16, "bold"))
    title_label.pack(side=tk.LEFT, padx=10, pady=10)

    # Cargamos los íconos para mensajes (estáticos)
    global own_icon_photo, other_icon_photo
    try:
        own_img = Image.open("perfil.jpg")
        own_img = own_img.resize((20, 20), Image.Resampling.LANCZOS)
        own_icon_photo = ImageTk.PhotoImage(own_img)
    except Exception as e:
        print("Error al cargar own_icon:", e)
        own_icon_photo = None

    try:
        other_img = Image.open("perfil2.jpg")
        other_img = other_img.resize((20, 20), Image.Resampling.LANCZOS)
        other_icon_photo = ImageTk.PhotoImage(other_img)
    except Exception as e:
        print("Error al cargar other_icon:", e)
        other_icon_photo = None

    # -------------------------
    # Área de chat con scroll y estilos
    # -------------------------
    chat_frame = tk.Frame(root, bg="#f0f0f0")
    chat_frame.pack(padx=10, pady=(5, 0), fill=tk.BOTH, expand=True)

    global chat_area
    chat_area = scrolledtext.ScrolledText(chat_frame, state='disabled', wrap=tk.WORD, font=("Helvetica", 12))
    chat_area.pack(fill=tk.BOTH, expand=True)
    chat_area.tag_config("own", background="#dcf8c6", foreground="black",
                         spacing1=5, spacing3=5, lmargin1=10, lmargin2=10)
    chat_area.tag_config("other", background="#ffffff", foreground="black",
                         spacing1=5, spacing3=5, lmargin1=10, lmargin2=10)

    # -------------------------
    # Área de entrada (sin ícono)
    # -------------------------
    input_frame = tk.Frame(root, bg="#f0f0f0")
    input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

    global message_entry
    message_entry = tk.Entry(input_frame, font=("Helvetica", 12))
    message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
    message_entry.bind("<Return>", send_message)

    send_button = tk.Button(input_frame, text="Enviar", command=send_message,
                            font=("Helvetica", 12), bg="#4CAF50", fg="white")
    send_button.pack(side=tk.LEFT, padx=(0, 5))

    history_button = tk.Button(root, text="Ver Historial", command=save_and_open_history,
                                font=("Helvetica", 12), bg="#2196F3", fg="white")
    history_button.pack(side=tk.BOTTOM, pady=(0, 5))

def receive_messages(sock, chat_area):
    """Recibe mensajes del servidor y los muestra con el ícono correspondiente."""
    while True:
        try:
            message = sock.recv(1024).decode()
            if not message:
                break
            parts = message.split(":", 1)
            if len(parts) >= 2:
                sender = parts[0].strip()
            else:
                sender = "Desconocido"

            chat_area.config(state='normal')
            if sender == username:
                if own_icon_photo:
                    chat_area.image_create(tk.END, image=own_icon_photo)
                chat_area.insert(tk.END, " " + message + "\n", "own")
            else:
                if other_icon_photo:
                    chat_area.image_create(tk.END, image=other_icon_photo)
                chat_area.insert(tk.END, " " + message + "\n", "other")
            chat_area.config(state='disabled')
            chat_area.see(tk.END)
        except Exception as e:
            print("Error al recibir mensaje:", e)
            break

def send_message(event=None):
    """Envía el mensaje escrito y lo muestra con el ícono del usuario actual."""
    message = message_entry.get()
    if message:
        full_message = f"{username}: {message}"
        try:
            sock.send(full_message.encode())
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo enviar el mensaje: {e}")
            return
        message_entry.delete(0, tk.END)
        chat_area.config(state='normal')
        if own_icon_photo:
            chat_area.image_create(tk.END, image=own_icon_photo)
        chat_area.insert(tk.END, " " + full_message + "\n", "own")
        chat_area.config(state='disabled')
        chat_area.see(tk.END)

def save_and_open_history():
    """Guarda el historial del chat en un archivo .txt y lo abre con el editor por defecto."""
    try:
        with open("chat_history.txt", "w", encoding="utf-8") as f:
            history = chat_area.get("1.0", tk.END)
            f.write(history)
        if sys.platform.startswith('win'):
            os.startfile("chat_history.txt")
        elif sys.platform.startswith('darwin'):
            os.system("open chat_history.txt")
        else:
            os.system("xdg-open chat_history.txt")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir el historial: {e}")

def on_closing():
    try:
        if sock:
            sock.close()
    except:
        pass
    root.destroy()
    sys.exit()

# ==============================
# MAIN: Inicio de la aplicación
# ==============================
root = tk.Tk()
root.withdraw()  # Oculta la ventana principal hasta obtener login

show_login(root)  # Solicita usuario e IP

build_chat_ui(root)  # Construye la interfaz del chat

root.deiconify()  # Muestra la ventana principal

# Conectar con el servidor
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_port = 5000
try:
    sock.connect((server_ip, server_port))
except Exception as e:
    messagebox.showerror("Error", f"No se pudo conectar al servidor: {e}")
    sys.exit()

# Iniciar hilo para recibir mensajes
thread = threading.Thread(target=receive_messages, args=(sock, chat_area))
thread.daemon = True
thread.start()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
