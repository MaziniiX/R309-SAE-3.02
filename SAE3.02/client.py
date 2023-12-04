import socket
import threading

HOST = '127.0.0.1'
PORT = 12345

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client_socket.connect((HOST, PORT))
except socket.error as e:
    print(f"Connection failed: {e}")
    exit()

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

def listen_for_messages():
    while True:
        try:
            message = receive_message(client_socket)
            if message:
                print(f"Received: {message.decode()}")
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

# Start a thread to listen for messages
message_listener = threading.Thread(target=listen_for_messages)
message_listener.start()

# Send and receive messages
while True:
    user_input = input("Enter a message (or 'exit' to quit): ")
    if user_input.lower() == 'exit':
        break
    send_message(client_socket, user_input)

# Close the connection
client_socket.close()
