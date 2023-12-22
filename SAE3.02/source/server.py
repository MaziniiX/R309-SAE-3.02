import socket
import threading
import sys
import bcrypt
import mysql.connector
from datetime import datetime, timedelta

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


def handle_client(client_socket, addr):
    """
    Handles communication with a connected client.

    Args:
        client_socket (socket.socket): The client's socket.
        addr (tuple): The client's address.

    Returns:
        None
    """
    print(f"Accepted connection from {addr}")

    try:
        # Send a welcome message to the client
        welcome_message = "login_signup"
        send_message(client_socket, welcome_message)

        # Wait for the client's choice
        choice = receive_message(client_socket).decode()

        username = None

        if choice == "login":
            username = handle_login(client_socket)
        elif choice == "signup":
            username = handle_signup(client_socket)
        else:
            # Invalid choice, close the connection or handle accordingly
            send_message(client_socket, "Invalid choice. Closing connection.")
            client_socket.close()

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
            if username and username in client_events:
                del client_events[username]
        # Close the connection
        print(f"Connection from {addr} closed.")
        client_socket.close()

def is_user_kicked(username):
    """
    Check if a user is currently kicked from the server.

    Args:
        username (str): The username to check.
        
    Returns:
        bool: True if the user is kicked, False otherwise.
    """
    cursor.execute("""
        SELECT username FROM kicked_users WHERE username = %s AND release_time > NOW()
    """, (username,))
    return cursor.fetchone() is not None


def is_user_banned(username):
    """
    Check if a user is currently banned from the server.

    Args:
        username (str): The username to check.

    Returns:
        bool: True if the user is banned, False otherwise.
    """
    cursor.execute("""
        SELECT username FROM banned_users WHERE username = %s
    """, (username,))
    return cursor.fetchone() is not None


def handle_login(client_socket):
    """
    Handle the login process for a client.

    Args:
        client_socket (socket.socket): The client's socket.

    Returns:
        str or None: The username if login is successful, None otherwise.
    """
    addr = client_socket.getpeername()
    # User Authentication
    username = receive_message(client_socket).decode()
    password = receive_message(client_socket).decode()

    if authenticate_user(username, password):
        print(f"Authentication successful for {username}")
        send_message(client_socket, b"LOGIN_SUCCESS")
        update_user_ip(username, addr[0])  # Update user's IP address
        return username
    else:
        print(f"Authentication failed for {username}")
        send_message(client_socket, b"LOGIN_FAILURE")
        return None

def authenticate_user(username, password):
    """
    Authenticate a user with the provided username and password.

    Args:
        username (str): The username to authenticate.
        password (str): The password to check.

    Returns:
        bool: True if authentication is successful, False otherwise.
    """
    cursor.execute("SELECT username, password_hash FROM users WHERE username = %s", (username,))
    user_data = cursor.fetchone()

    if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data[1].encode('utf-8')):
        return True
    return False

def handle_signup(client_socket):
    """
    Handle the user registration process for a client.

    Args:
        client_socket (socket.socket): The client's socket.

    Returns:
        str or None: The username if registration is successful, None otherwise.
    """
    addr = client_socket.getpeername()
    # User registration
    username = receive_message(client_socket).decode()
    password = receive_message(client_socket).decode()

    if register_user(username, password, addr[0]):  # Pass the IP address to the function
        print(f"Registration successful for {username}")
        send_message(client_socket, b"SIGNUP_SUCCESS")
        return username
    else:
        print(f"Registration failed for {username}")
        send_message(client_socket, b"SIGNUP_FAILURE")
        return None

def register_user(username, password, ip_address):
    """
    Register a new user with the provided username, password, and IP address.

    Args:
        username (str): The username for the new user.
        password (str): The password for the new user.
        ip_address (str): The IP address of the new user.

    Returns:
        bool: True if registration is successful, False otherwise.
    """
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
    """
    Run the admin console, allowing the administrator to input commands.

    Returns:
        None
    """
    while True:
        admin_input = input("Admin console: ")
        if admin_input.startswith(ADMIN_COMMAND_PREFIX):
            process_admin_command(admin_input[len(ADMIN_COMMAND_PREFIX):])

def process_admin_command(admin_command):
    """
    Process an admin command received from the admin console.

    Args:
        admin_command (str): The admin command to process.

    Returns:
        None
    """
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
    """
    Kick a user from the server for a specified duration.

    Args:
        target_user (str): The username of the user to be kicked.
        duration (str): The duration of the kick in seconds.

    Returns:
        None
    """
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
    """
    Retrieve the IP address associated with a given username.

    Args:
        username (str): The username for which to retrieve the IP address.

    Returns:
        str or None: The IP address of the user, or None if not found.
    """
    cursor.execute("SELECT ip_address FROM users WHERE username = %s", (username,))
    ip_address = cursor.fetchone()
    if ip_address:
        return ip_address[0]
    return None

def update_user_ip(username, ip_address):
    """
    Update the IP address associated with a given username.

    Args:
        username (str): The username for which to update the IP address.
        ip_address (str): The new IP address.

    Returns:
        None
    """
    try:
        cursor.execute("""
            UPDATE users SET ip_address = %s WHERE username = %s
        """, (ip_address, username))
        db.commit()
        print(f"User {username}'s IP address updated to {ip_address}")
    except Exception as e:
        print(f"Error updating user's IP address: {e}")

def ban_user(target_user):
    """
    Ban a user from the server indefinitely.

    Args:
        target_user (str): The username of the user to be banned.

    Returns:
        None
    """
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
    """
    Unban a user from the server.

    Args:
        target_user (str): The username of the user to be unbanned.

    Returns:
        None
    """
    # Remove the user's record from the banned_users table
    cursor.execute("DELETE FROM banned_users WHERE username = %s", (target_user,))
    db.commit()

    # Send a message to inform about the unban
    message = f"You have been unbanned. You can now reconnect to the server."
    send_private_message("Admin", target_user, message)

    print(f"User {target_user} unbanned")

# Helper function to close a user's socket
def close_user_socket(username):
    """
    Close the socket connection for a kicked or banned user.

    Args:
        username (str): The username of the user whose socket to close.

    Returns:
        None
    """
    user_socket = get_user_socket(username)
    if user_socket:
        try:
            user_socket.close()
        except Exception as e:
            print(f"Error closing connection for kicked/banned user {username}: {e}")


def get_user_socket(username):
    """
    Retrieve the socket associated with a given username.

    Args:
        username (str): The username for which to retrieve the socket.

    Returns:
        socket.socket or None: The socket of the user, or None if not found.
    """
    with lock:
        for client in connected_clients:
            if client["username"] == username:
                return client["socket"]
    return None

def kill_server():
    """
    Initiate a server shutdown process.

    Sends a broadcast message to all clients, announces the server shutdown,
    and schedules the actual server shutdown after a 10-second delay.

    Returns:
        None
    """
    broadcast_message("Admin", "The server will shut down in 10 seconds. Save your work!")
    print("Server will shut down in 10 seconds. Save your work!")

    timer = threading.Timer(10, shutdown_server)
    timer.start()

def shutdown_server():
    """
    Perform the actual shutdown of the server.

    Closes the server socket, disconnects from the database, and exits the application.

    Returns:
        None
    """
    print("Server shut down.")
    server_socket.close()
    close_database_connection()
    sys.exit()

def send_message(sock, message):
    """
    Send a message to a specified socket.

    Args:
        sock (socket.socket): The socket to which the message will be sent.
        message (str): The message to send.

    Returns:
        None
    """
    message_bytes = message.encode('utf-8') if isinstance(message, str) else message
    sock.send(message_bytes)

def receive_message(sock):
    """
    Receive a message from a specified socket.

    Args:
        sock (socket.socket): The socket from which to receive the message.

    Returns:
        bytes: The received message.
    """
    return sock.recv(4096)

def broadcast_message(sender_username, message):
    """
    Broadcast a message to all connected clients.

    Args:
        sender_username (str): The username of the sender.
        message (str): The message to broadcast.

    Returns:
        None
    """
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
    """
    Store a public message in the database.

    Args:
        sender (str): The username of the message sender.
        content (str): The content of the message.
        sender_ip (str): The IP address of the message sender.

    Returns:
        None
    """
    cursor.execute("""
                INSERT INTO messages (sender_username, content, sender_ip)
                VALUES (%s, %s, %s)
            """, (sender, content, sender_ip))
    db.commit()

def store_private_message(sender, receiver, content, sender_ip):
    """
    Store a private message in the database.

    Args:
        sender (str): The username of the message sender.
        receiver (str): The username of the message receiver.
        content (str): The content of the message.
        sender_ip (str): The IP address of the message sender.

    Returns:
        None
    """
    cursor.execute("""
                INSERT INTO private_messages (sender_username, receiver_username, content, sender_ip)
                VALUES (%s, %s, %s, %s)
            """, (sender, receiver, content, sender_ip))
    db.commit()

def send_private_message(sender, receiver, content):
    """
    Send a private message to a specific user.

    Args:
        sender (str): The username of the message sender.
        receiver (str): The username of the message receiver.
        content (str): The content of the private message.

    Returns:
        None
    """
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
    """
    Close the connection to the database.

    Returns:
        None
    """
    cursor.close()
    db.close()


if __name__ == "__main__":
        # Initialize database connection and create tables
    db = mysql.connector.connect(**DB_CONFIG)
    cursor = db.cursor()
    
    for table_name, table_query in TABLES.items():
        cursor.execute(table_query)
    db.commit()
    
    # Initialize server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((HOST, PORT))
    except socket.error as e:
        print(f"Failed to bind: {e}")
        sys.exit()
    
    server_socket.listen()
    print(f"Server listening on {HOST}:{PORT}")
    
    # Global variables
    connected_clients = []
    client_events = {}
    lock = threading.Lock()
    
    ADMIN_COMMAND_PREFIX = ""
    
    admin_console_thread = threading.Thread(target=admin_console)
    admin_console_thread.start()

    while True:
        client_socket, addr = server_socket.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_handler.start()
