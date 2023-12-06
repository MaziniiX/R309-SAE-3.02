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
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()

# Check if messages table exists, if not, create it
cursor.execute("SHOW TABLES LIKE 'messages'")
if not cursor.fetchone():
    cursor.execute("""
        CREATE TABLE messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sender_username VARCHAR(50) NOT NULL,
            receiver_username VARCHAR(50) NOT NULL,
            content TEXT NOT NULL,
            sender_ip VARCHAR(15) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_username) REFERENCES users(username),
            FOREIGN KEY (receiver_username) REFERENCES users(username)
        )
    """)
    db.commit()

# Check if kicks table exists, if not, create it
cursor.execute("SHOW TABLES LIKE 'kicks'")
if not cursor.fetchone():
    cursor.execute("""
        CREATE TABLE kicks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            admin_username VARCHAR(50) NOT NULL,
            target_username VARCHAR(50) NOT NULL,
            duration VARCHAR(20) NOT NULL,
            kicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (admin_username) REFERENCES users(username),
            FOREIGN KEY (target_username) REFERENCES users(username)
        )
    """)
    db.commit()

# Check if bans table exists, if not, create it
cursor.execute("SHOW TABLES LIKE 'bans'")
if not cursor.fetchone():
    cursor.execute("""
        CREATE TABLE bans (
            id INT AUTO_INCREMENT PRIMARY KEY,
            admin_username VARCHAR(50) NOT NULL,
            target_username VARCHAR(50) NOT NULL,
            banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (admin_username) REFERENCES users(username),
            FOREIGN KEY (target_username) REFERENCES users(username)
        )
    """)
    db.commit()

# Check if kills table exists, if not, create it
cursor.execute("SHOW TABLES LIKE 'kills'")
if not cursor.fetchone():
    cursor.execute("""
        CREATE TABLE kills (
            id INT AUTO_INCREMENT PRIMARY KEY,
            admin_username VARCHAR(50) NOT NULL,
            killed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (admin_username) REFERENCES users(username)
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

            # Check if the authenticated user is an admin
            is_admin = check_admin(username)

            # Add the client socket to the list
            with lock:
                connected_clients.append({"socket": client_socket, "username": username, "is_admin": is_admin})

            # Receive and broadcast messages from the client
            while True:
                data = receive_message(client_socket)
                if not data:
                    break

                print(f"Received from {username}: {data.decode()}")

                # Process admin commands
                if is_admin and data.startswith("/"):
                    process_admin_command(username, data)

                else:
                    # Store the message in the database
                    store_message(username, "All", data.decode(), addr[0])

                    # Check if it is a private message
                    if data.startswith("/pm"):
                        _, receiver, pm_content = data.split(" ", 2)
                        send_private_message(username, receiver, pm_content)

                    else:
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

def check_admin(username):
    cursor.execute("SELECT is_admin FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()
    return result and result[0] == 1

def process_admin_command(admin_username, command):
    # Process admin commands
    if command.startswith("/kick"):
        _, target_user, duration = command.split(" ", 2)
        kick_user(admin_username, target_user, duration)

    elif command.startswith("/ban"):
        _, target_user, _ = command.split(" ", 2)
        ban_user(admin_username, target_user)

    elif command.startswith("/kill"):
        kill_server(admin_username)

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
