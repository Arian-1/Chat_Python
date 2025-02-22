# Chat App Project

Este repositorio contiene una aplicación de chat compuesta por un **servidor** y uno o más **clientes**.

- El **servidor** se encarga de recibir mensajes de los clientes, reenviarlos y almacenarlos en una base de datos SQLite (`chat_history.db`).
- El **cliente** es una aplicación gráfica (Tkinter) que se conecta al servidor para enviar y recibir mensajes.

> **Nota:**  
> El servidor debe ejecutarse utilizando Docker para garantizar un entorno consistente. El cliente se puede ejecutar de forma local.

## Requisitos

### Generales
- **Python 3.x**

### Servidor (obligatorio usar Docker)
- **Docker Desktop** instalado y corriendo
- Construye y ejecuta el ambiente con:
- docker build -t chat-server .
- docker run -d -p 5000:5000 --name servidor_chat chat-server

### Cliente (ejecución local)
- **Tkinter** (en Windows y macOS viene preinstalado)
- **Pillow** (para el manejo de imágenes)  
  Instala con:
  pip install Pillow
