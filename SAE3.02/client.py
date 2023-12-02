import socket

HOST = '127.0.0.1'
PORT = 12345

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client_socket.connect((HOST, PORT))
except socket.error as e:
    print(f"Connection failed: {e}")
    exit()


def send_message(sock, message):
    message_length = len(message)
    header = f"{message_length:<10}".encode()
    sock.send(header + message.encode())


def receive_message(sock):
    header = sock.recv(10)
    if not header:
        return None

    message_length = int(header.decode().strip())
    return sock.recv(message_length)


try:
    # Receive and print the welcome message from the server
    welcome_message = receive_message(client_socket)
    print(f"Server: {welcome_message.decode()}")

    while True:
        # Send a message to the server
        client_message = input("Enter your message (or 'exit' to quit): ")
        if client_message.lower() == 'exit':
            break

        send_message(client_socket, client_message)

except Exception as e:
    print(f"Error during communication: {e}")

finally:
    # Close the connection
    client_socket.close()
