import socket
import threading
import bcrypt
import mysql.connector

# Connect to MySQL database
db = mysql.connector.connect(
    host="192.168.231.128",
    user="admin",
    password="toto",
    database="sae302"
)

cursor = db.cursor()

HOST = '0.0.0.0'
PORT = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    server_socket.bind((HOST, PORT))
except socket.error as e:
    print(f"Failed to bind: {e}")
    exit()

server_socket.listen(5)
print(f"Server listening on {HOST}:{PORT}")

# List to keep track of connected client sockets
connected_clients = []
lock = threading.Lock()

# Check if users table exists, if not, create it
cursor.execute("SHOW TABLES LIKE 'users'")
if not cursor.fetchone():
    cursor.execute("""
        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()

def handle_client(client_socket, addr):
    print(f"Accepted connection from {addr}")

    try:
        # Send a welcome message to the client
        welcome_message = "Welcome to the server! Please log in."
        send_message(client_socket, welcome_message)

        # User Authentication
        username = receive_message(client_socket).decode()
        password = receive_message(client_socket).decode()

        if authenticate_user(username, password):
            print(f"Authentication successful for {username}")
            # Add the client socket to the list
            with lock:
                connected_clients.append({"socket": client_socket, "username": username})

            # Receive and broadcast messages from the client
            while True:
                data = receive_message(client_socket)
                if not data:
                    break

                print(f"Received from {username}: {data.decode()}")

                # Broadcast the message to all connected clients
                broadcast_message(client_socket, data)

        else:
            print(f"Authentication failed for {username}")
            error_message = "Authentication failed. Closing connection."
            send_message(client_socket, error_message)

    except Exception as e:
        print(f"Error handling connection from {addr}: {e}")

    finally:
        # Remove the client socket from the list
        with lock:
            connected_clients[:] = [c for c in connected_clients if c["socket"] != client_socket]

        # Close the connection
        print(f"Connection from {addr} closed.")
        client_socket.close()

def send_message(sock, message):
    message_bytes = message.encode('utf-8') if isinstance(message, str) else message
    message_length = len(message_bytes)
    header = f"{message_length:<10}".encode()
    sock.send(header + message_bytes)

def receive_message(sock):
    header = sock.recv(10)
    if not header:
        return None

    message_length = int(header.decode().strip())
    return sock.recv(message_length)

def broadcast_message(sender_socket, message):
    with lock:
        for client in connected_clients:
            # Do not send the message back to the sender
            if client["socket"] != sender_socket:
                try:
                    send_message(client["socket"], message)
                except Exception as e:
                    print(f"Error broadcasting to a client: {e}")

def authenticate_user(username, password):
    cursor.execute("SELECT username, password_hash FROM users WHERE username = %s", (username,))
    user_data = cursor.fetchone()

    if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data[1].encode('utf-8')):
        return True
    return False

# Close the database connection when the server stops
def close_database_connection():
    cursor.close()
    db.close()

# Accept and handle incoming connections
while True:
    client_socket, addr = server_socket.accept()
    client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
    client_handler.start()
