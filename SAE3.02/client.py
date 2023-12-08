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
    sock.send(message_bytes)

def receive_message(sock):
    return sock.recv(4096)  # Adjust the buffer size as needed

# Start a thread to listen for messages
def listen_for_messages():
    while True:
        try:
            message = receive_message(client_socket)
            if message:
                print(message.decode())
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

# User registration or login
print(receive_message(client_socket).decode())  # Welcome message
choice = "login" #input("Choose 'login' or 'signup': ").lower()
send_message(client_socket, choice)

if choice == 'login' or choice == 'signup':
    # User Authentication or Registration
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    send_message(client_socket, username)
    send_message(client_socket, password)

    # Receive response from the server
    response = receive_message(client_socket).decode()

    if response == "LOGIN_SUCCESS" or response == "SIGNUP_SUCCESS":
        print("Authentication/Registration successful. You can now send messages.")
    else:
        print(f"Authentication/Registration failed: {response}")
        client_socket.close()
        exit()
else:
    print("Invalid choice. Exiting.")
    client_socket.close()
    exit()

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
