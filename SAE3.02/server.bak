import socket
import threading
import bcrypt
import mysql.connector
from datetime import datetime, timedelta
import time

HOST = '0.0.0.0'
PORT = 12345
BUFFER_SIZE = 4096

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "admin",
    "password": "toto",
    "database": "sae302",
}

TABLES = {
    "users": """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(100) NOT NULL,
            ip_address VARCHAR(15),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """,
    "messages": """
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sender_username VARCHAR(50) NOT NULL,
            content TEXT NOT NULL,
            sender_ip VARCHAR(15) NOT NULL,
            sended_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_username) REFERENCES users(username)
        )
    """,
    "private_messages": """
        CREATE TABLE IF NOT EXISTS private_messages (
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
    "kicked_users": """
           CREATE TABLE IF NOT EXISTS kicked_users (
               username VARCHAR(50) NOT NULL,
               ip_address VARCHAR(15) NOT NULL,
               kicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
               release_time TIMESTAMP NOT NULL,
               FOREIGN KEY (username) REFERENCES users(username)
           )
       """,
    "banned_users": """
           CREATE TABLE IF NOT EXISTS banned_users (
               username VARCHAR(50) NOT NULL,
               ip_address VARCHAR(15) NOT NULL,
               banned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
               FOREIGN KEY (username) REFERENCES users(username)
           )
       """
}

db = mysql.connector.connect(**DB_CONFIG)
cursor = db.cursor()

for table_name, table_query in TABLES.items():
    cursor.execute(table_query)
db.commit()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server_socket.bind((HOST, PORT))
except socket.error as e:
    print(f"Failed to bind: {e}")
    exit()

server_socket.listen(5)
print(f"Server listening on {HOST}:{PORT}")

connected_clients = []
client_events = {}
lock = threading.Lock()

ADMIN_COMMAND_PREFIX = ""

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
            username = handle_signup(client_socket, addr)
        else:
            # Invalid action, close the connection or handle accordingly
            print("Invalid action. Closing connection.")
            client_socket.close()
            return

        if username:
            # Check if the user is in the kicked or banned list
            if is_user_kicked(username) or is_user_banned(username):
                print(f"User {username} is kicked. Closing connection.")
                send_message(client_socket, "You are currently kicked.")
                client_socket.close()
                return
            elif is_user_banned(username):
                print(f"User {username} is banned. Closing connection.")
                send_message(client_socket, "You are currently banned.")
                client_socket.close()
                return

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
                data = data.decode()
                # Process private messages
                if data.startswith("/pm"):
                    _, receiver, pm_content = data.split(" ", 2)
                    send_private_message(username, receiver, pm_content)
                    store_private_message(username, receiver, pm_content, addr[0])

                else:
                    # Check if the message is a public message and not sent by the same user
                    if not data.startswith("/"):
                        # Broadcast the message to all connected clients (excluding the sender)
                        broadcast_message(username, data)
                        # Store the message in the database (public message)
                        store_message(username, data, addr[0])

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


def is_user_kicked(username):
    # Check if the user is in the kicked list
    cursor.execute("""
        SELECT username FROM kicked_users WHERE username = %s AND release_time > NOW()
    """, (username,))
    return cursor.fetchone() is not None


def is_user_banned(username):
    # Check if the user is in the banned list
    cursor.execute("""
        SELECT username FROM banned_users WHERE username = %s
    """, (username,))
    return cursor.fetchone() is not None


def handle_login(client_socket):
    addr = client_socket.getpeername()
    # User Authentication
    username = receive_message(client_socket).decode()
    password = receive_message(client_socket).decode()

    if authenticate_user(username, password):
        print(f"Authentication successful for {username}")
        send_message(client_socket, "LOGIN_SUCCESS")
        update_user_ip(username, addr[0])  # Update user's IP address
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

def handle_signup(client_socket, addr):
    # User registration
    username = receive_message(client_socket).decode()
    password = receive_message(client_socket).decode()

    if register_user(username, password, addr[0]):  # Pass the IP address to the function
        print(f"Registration successful for {username}")
        send_message(client_socket, "SIGNUP_SUCCESS")
        return username
    else:
        print(f"Registration failed for {username}")
        send_message(client_socket, "SIGNUP_FAILURE")
        return None

def register_user(username, password, ip_address):
    # Hash the password before storing it
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        cursor.execute("""
            INSERT INTO users (username, password_hash, ip_address)
            VALUES (%s, %s, %s)
        """, (username, hashed_password, ip_address))
        db.commit()
        return True
    except Exception as e:
        print(f"Error registering user: {e}")
        return False

def admin_console():
    while True:
        admin_input = input("Admin console: ")
        if admin_input.startswith(ADMIN_COMMAND_PREFIX):
            process_admin_command(admin_input[len(ADMIN_COMMAND_PREFIX):])

def process_admin_command(admin_command):
    if admin_command.startswith("/kick"):
        _, target_user, duration = admin_command.split(" ", 2)
        kick_user(target_user, duration)
    elif admin_command.startswith("/ban"):
        _, target_user = admin_command.split(" ", 2)
        ban_user(target_user)
    elif admin_command.startswith("/unban"):
        _, target_user = admin_command.split(" ", 1)
        unban_user(target_user)
    elif admin_command.startswith("/kill"):
        kill_server()
    else:
        print("Invalid admin command")

def kick_user(target_user, duration):
    user_ip = get_user_ip(target_user)

    if user_ip:
        kick_duration = int(duration)
        release_time = datetime.now() + timedelta(seconds=kick_duration)

        print(f"target_user: {target_user}, user_ip: {user_ip}, release_time: {release_time}")
        cursor.execute("""
            INSERT INTO kicked_users (username, ip_address, release_time)
            VALUES (%s, %s, %s)
        """, (target_user, str(user_ip), release_time))

        db.commit()

        message = f"You have been kicked from the server for {duration} seconds. You can rejoin after {release_time}"
        send_private_message("Admin", target_user, message)

        close_user_socket(target_user)

        print(f"User {target_user} kicked for {duration} seconds. They can rejoin after {release_time}")
    else:
        print(f"Error: User {target_user} not found.")

def get_user_ip(username):
    cursor.execute("SELECT ip_address FROM users WHERE username = %s", (username,))
    ip_address = cursor.fetchone()
    if ip_address:
        return ip_address[0]
    return None

def update_user_ip(username, ip_address):
    try:
        cursor.execute("""
            UPDATE users SET ip_address = %s WHERE username = %s
        """, (ip_address, username))
        db.commit()
        print(f"User {username}'s IP address updated to {ip_address}")
    except Exception as e:
        print(f"Error updating user's IP address: {e}")

def ban_user(target_user):
    user_ip = get_user_ip(target_user)
    user_socket = get_user_socket(target_user)

    cursor.execute("""
        INSERT INTO banned_users (username, ip_address)
        VALUES (%s, %s)
    """, (target_user, user_ip))
    db.commit()

    message = "You have been banned from the server indefinitely."
    send_private_message("Admin", target_user, message)

    close_user_socket(target_user)

    print(f"User {target_user} banned indefinitely")

def unban_user(target_user):
    # Remove the user's record from the banned_users table
    cursor.execute("DELETE FROM banned_users WHERE username = %s", (target_user,))
    db.commit()

    # Send a message to inform about the unban
    message = f"You have been unbanned. You can now reconnect to the server."
    send_private_message("Admin", target_user, message)

    # Implement additional logic as needed
    print(f"User {target_user} unbanned")

# Helper function to close a user's socket
def close_user_socket(username):
    user_socket = get_user_socket(username)
    if user_socket:
        try:
            user_socket.close()
        except Exception as e:
            print(f"Error closing connection for kicked/banned user {username}: {e}")


def get_user_socket(username):
    with lock:
        for client in connected_clients:
            if client["username"] == username:
                return client["socket"]
    return None

def kill_server():
    broadcast_message("Admin", "The server will shut down in 10 seconds. Save your work!")
    print("Server will shut down in 10 seconds. Save your work!")

    timer = threading.Timer(10, shutdown_server)
    timer.start()

def shutdown_server():
    print("Server shut down.")
    server_socket.close()
    close_database_connection()
    exit()

def send_message(sock, message):
    message_bytes = message.encode('utf-8') if isinstance(message, str) else message
    sock.send(message_bytes)

def receive_message(sock):
    return sock.recv(4096)

def broadcast_message(sender_username, message):
    with lock:
        for client in connected_clients:
            if client["username"] != sender_username:
                try:
                    send_message(client["socket"], message)
                except Exception as e:
                    print(f"Error broadcasting to a client: {e}")

        for username, event in client_events.items():
            if username != sender_username:
                event.set()

def store_message(sender, content, sender_ip):
    cursor.execute("""
                INSERT INTO messages (sender_username, content, sender_ip)
                VALUES (%s, %s, %s)
            """, (sender, content, sender_ip))
    db.commit()

def store_private_message(sender, receiver, content, sender_ip):
    cursor.execute("""
                INSERT INTO private_messages (sender_username, receiver_username, content, sender_ip)
                VALUES (%s, %s, %s, %s)
            """, (sender, receiver, content, sender_ip))
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

def close_database_connection():
    cursor.close()
    db.close()

admin_console_thread = threading.Thread(target=admin_console)
admin_console_thread.start()

while True:
    client_socket, addr = server_socket.accept()
    client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
    client_handler.start()
