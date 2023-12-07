import socket
import threading
import bcrypt
import mysql.connector

# Constants
HOST = '0.0.0.0'
PORT = 12345
BUFFER_SIZE = 4096

# Database configuration
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "admin",
    "password": "toto",
    "database": "sae302",
}

# Database setup
TABLES = {
    "users": """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    "messages": """
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sender_username VARCHAR(50) NOT NULL,
            receiver_username VARCHAR(50) NOT NULL,
            content TEXT NOT NULL,
            sender_ip VARCHAR(15) NOT NULL,
            sended_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_username) REFERENCES users(username),
            FOREIGN KEY (receiver_username) REFERENCES users(username)
        )
    """,
    "kicks": """
        CREATE TABLE IF NOT EXISTS kicks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            admin_username VARCHAR(50) NOT NULL,
            target_username VARCHAR(50) NOT NULL,
            duration VARCHAR(20) NOT NULL,
            kicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (admin_username) REFERENCES users(username),
            FOREIGN KEY (target_username) REFERENCES users(username)
        )
    """,
    "bans": """
        CREATE TABLE IF NOT EXISTS bans (
            id INT AUTO_INCREMENT PRIMARY KEY,
            admin_username VARCHAR(50) NOT NULL,
            target_username VARCHAR(50) NOT NULL,
            banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (admin_username) REFERENCES users(username),
            FOREIGN KEY (target_username) REFERENCES users(username)
        )
    """,
    "kills": """
        CREATE TABLE IF NOT EXISTS kills (
            id INT AUTO_INCREMENT PRIMARY KEY,
            admin_username VARCHAR(50) NOT NULL,
            killed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (admin_username) REFERENCES users(username)
        )
    """,
}

# Database connection
db = mysql.connector.connect(**DB_CONFIG)
cursor = db.cursor()

# Create tables if not exists
for table_name, table_query in TABLES.items():
    cursor.execute(table_query)
db.commit()

# Server setup
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
client_events = {}
lock = threading.Lock()

# Admin command prefix
ADMIN_COMMAND_PREFIX = "/"

def handle_client(client_socket, addr):
    print(f"Accepted connection from {addr}")

    try:
        # Send a welcome message to the client
        welcome_message = "Welcome to the server! Would you like to login or signup?"
        send_message(client_socket, welcome_message)

        # Check if the client wants to log in or sign up
        action = receive_message(client_socket).decode()

        username = None

        if action == "login":
            username = handle_login(client_socket)
        elif action == "signup":
            username = handle_signup(client_socket)
        else:
            # Invalid action, close the connection or handle accordingly
            print("Invalid action. Closing connection.")
            client_socket.close()
            return

        if username:
            # Create an event for the client
            client_event = threading.Event()
            with lock:
                connected_clients.append({"socket": client_socket, "username": username, "event": client_event})
                client_events[username] = client_event

            # Continue with the rest of your logic for handling messages
            while True:
                data = receive_message(client_socket)
                if not data:
                    break

                print(f"Received from {username}: {data.decode()}")

                # Broadcast the message to all connected clients
                broadcast_message(username, data)

    except Exception as e:
        print(f"Error handling connection from {addr}: {e}")

    finally:
        # Remove the client socket from the list
        with lock:
            connected_clients[:] = [c for c in connected_clients if c["socket"] != client_socket]
            if username in client_events:
                del client_events[username]

        # Close the connection
        print(f"Connection from {addr} closed.")
        client_socket.close()

# Helper function to handle user login
def handle_login(client_socket):
    # User Authentication
    username = receive_message(client_socket).decode()
    password = receive_message(client_socket).decode()

    if authenticate_user(username, password):
        print(f"Authentication successful for {username}")
        send_message(client_socket, "LOGIN_SUCCESS")
        return username
    else:
        print(f"Authentication failed for {username}")
        send_message(client_socket, "LOGIN_FAILURE")
        return None

def authenticate_user(username, password):
    cursor.execute("SELECT username, password_hash FROM users WHERE username = %s", (username,))
    user_data = cursor.fetchone()

    if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data[1].encode('utf-8')):
        return True
    return False

# Helper function to handle user signup
def handle_signup(client_socket):
    # User registration
    username = receive_message(client_socket).decode()
    password = receive_message(client_socket).decode()

    if register_user(username, password):
        print(f"Registration successful for {username}")
        send_message(client_socket, "SIGNUP_SUCCESS")
        return username
    else:
        print(f"Registration failed for {username}")
        send_message(client_socket, "SIGNUP_FAILURE")
        return None

# Helper function to register a new user
def register_user(username, password):
    # Hash the password before storing it
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        cursor.execute("""
            INSERT INTO users (username, password_hash)
            VALUES (%s, %s)
        """, (username, hashed_password))
        db.commit()
        return True
    except Exception as e:
        print(f"Error registering user: {e}")
        return False


# Admin command handling in the server console
def admin_console():
    while True:
        admin_input = input("Admin console: ")
        if admin_input.startswith(ADMIN_COMMAND_PREFIX):
            process_admin_command(admin_input[len(ADMIN_COMMAND_PREFIX):])

def process_admin_command(admin_command):
    # Process admin commands here
    if admin_command.startswith("/kick"):
        _, target_user, duration = admin_command.split(" ", 2)
        kick_user("Admin", target_user, duration)
    elif admin_command.startswith("/ban"):
        _, target_user, _ = admin_command.split(" ", 2)
        ban_user("Admin", target_user)
    elif admin_command.startswith("/kill"):
        kill_server("Admin")
    else:
        print("Invalid admin command")

def kick_user(admin_username, target_user, duration):
    cursor.execute("""
        INSERT INTO kicks (admin_username, target_username, duration)
        VALUES (%s, %s, %s)
    """, (admin_username, target_user, duration))
    db.commit()

    # Implement additional logic as needed
    print(f"User {target_user} kicked for {duration} by admin {admin_username}")

def ban_user(admin_username, target_user):
    cursor.execute("""
        INSERT INTO bans (admin_username, target_username)
        VALUES (%s, %s)
    """, (admin_username, target_user))
    db.commit()

    # Implement additional logic as needed
    print(f"User {target_user} banned indefinitely by admin {admin_username}")

def kill_server(admin_username):
    cursor.execute("""
        INSERT INTO kills (admin_username)
        VALUES (%s)
    """, (admin_username,))
    db.commit()

    # Implement additional logic as needed
    print(f"Server killed by admin {admin_username}")

def send_message(sock, message):
    message_bytes = message.encode('utf-8') if isinstance(message, str) else message
    sock.send(message_bytes)

def receive_message(sock):
    return sock.recv(4096)

def broadcast_message(sender_username, message):
    with lock:
        for client in connected_clients:
            # Do not send the message back to the sender
            if client["username"] != sender_username:
                try:
                    send_message(client["socket"], message)
                except Exception as e:
                    print(f"Error broadcasting to a client: {e}")

        # Set events for all clients except the sender
        for username, event in client_events.items():
            if username != sender_username:
                event.set()

def store_message(sender, receiver, content):
    cursor.execute("""
        INSERT INTO messages (sender_username, receiver_username, content)
        VALUES (%s, %s, %s)
    """, (sender, receiver, content))
    db.commit()

def send_private_message(sender, receiver, content):
    receiver_socket = None
    with lock:
        for client in connected_clients:
            if client["username"] == receiver:
                receiver_socket = client["socket"]
                break

    if receiver_socket:
        pm_message = f"DM from {sender}: {content}"
        send_message(receiver_socket, pm_message)
        store_message(sender, receiver, pm_message)

# Close the database connection when the server stops
def close_database_connection():
    cursor.close()
    db.close()

# Start the admin console thread
admin_console_thread = threading.Thread(target=admin_console)
admin_console_thread.start()

# Accept and handle incoming connections
while True:
    client_socket, addr = server_socket.accept()
    client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
    client_handler.start()