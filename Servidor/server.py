import socket
import threading
import sqlite3
import datetime

# Lista global de clientes conectados
clients = []

# Inicialización de la base de datos SQLite (chat_history.db)
conn = sqlite3.connect('chat_history.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        sender TEXT, 
        message TEXT, 
        timestamp TEXT
    )
''')
conn.commit()


def broadcast(message, sender_socket):
    """Envía el mensaje a todos los clientes excepto al que lo envió."""
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode())
            except Exception as e:
                print("Error al enviar mensaje:", e)
                client.close()
                if client in clients:
                    clients.remove(client)


def handle_client(client_socket):
    """Maneja la comunicación con cada cliente."""
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            # Se asume que el mensaje viene con formato "usuario: mensaje"
            parts = message.split(":", 1)
            if len(parts) >= 2:
                username = parts[0].strip()
                msg_text = parts[1].strip()
            else:
                username = "Desconocido"
                msg_text = message

            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # Almacena el mensaje en la base de datos
            cursor.execute("INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)",
                           (username, msg_text, timestamp))
            conn.commit()

            print(f"{timestamp} - {username}: {msg_text}")
            broadcast(message, client_socket)
        except Exception as e:
            print("Error:", e)
            break
    client_socket.close()
    if client_socket in clients:
        clients.remove(client_socket)


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5000))
    server.listen(5)
    print("Servidor de chat iniciado en el puerto 5000...")

    while True:
        client_socket, addr = server.accept()
        print("Nueva conexión desde:", addr)
        clients.append(client_socket)
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()


if __name__ == "__main__":
    main()
