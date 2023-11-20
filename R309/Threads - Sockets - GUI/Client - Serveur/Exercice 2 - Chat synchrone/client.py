import socket

host = '127.0.0.1'  # Adresse IP du serveur
port = 12345
flag = False

while not flag:
    client_socket = socket.socket()
    client_socket.connect((host, port))

    message = input("Write your message (leave with bye, close the server with arret): ")
    client_socket.send(message.encode())

    if message.lower() == 'bye' or message.lower() == 'arret':
        print("Client disconnection.")
        client_socket.close()
        flag = True

    reply = client_socket.recv(1024).decode()
    print("Reply from server :", reply)

    if reply.lower() == 'arret' or message.lower() == 'bye':
        print("Client disconnection")
        client_socket.close()
        flag = True

    client_socket.close()


