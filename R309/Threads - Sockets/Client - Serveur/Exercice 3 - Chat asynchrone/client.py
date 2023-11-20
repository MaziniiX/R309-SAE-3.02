import socket
import threading

host = '127.0.0.1'
port = 12345
flag = False

def receive_messages(client_socket):
    while True:
        reply = client_socket.recv(1024).decode()
        print("Reply from server:", reply)
        if reply.lower() == 'arret' or reply.lower() == 'bye':
            print("Client disconnection.")
            client_socket.close()
            break

client_socket = socket.socket()
client_socket.connect((host, port))

receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
receive_thread.start()

while not flag:
    message = input("Write your message (leave with bye, close the server with arret): ")
    client_socket.send(message.encode())

    if message.lower() == 'bye' or message.lower() == 'arret':
        print("Client disconnection.")
        client_socket.close()
        flag = True

client_socket.close()
