import socket
import threading

HOST = '0.0.0.0'  # Bind to all available network interfaces
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

def handle_client(client_socket, addr):
    print(f"Accepted connection from {addr}")

    try:
        # Send a welcome message to the client
        welcome_message = "Welcome to the server!"
        send_message(client_socket, welcome_message)

        # Add the client socket to the list
        with lock:
            connected_clients.append(client_socket)

        # Receive and broadcast messages from the client
        while True:
            data = receive_message(client_socket)
            if not data:
                break

            print(f"Received from {addr}: {data.decode()}")

            # Broadcast the message to all connected clients
            broadcast_message(client_socket, data)

    except Exception as e:
        print(f"Error handling connection from {addr}: {e}")

    finally:
        # Remove the client socket from the list
        with lock:
            connected_clients.remove(client_socket)

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
        for client_socket in connected_clients:
            # Do not send the message back to the sender
            if client_socket != sender_socket:
                try:
                    send_message(client_socket, message)
                except Exception as e:
                    print(f"Error broadcasting to a client: {e}")

# Accept and handle incoming connections
while True:
    client_socket, addr = server_socket.accept()
    client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
    client_handler.start()
