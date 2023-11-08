import socket

HOST = '127.0.0.1'
PORT = 65432

client_socket = socket.socket()
client_socket.connect((HOST, PORT))
message="Hello world"
client_socket.send(message.encode())
data = client_socket.recv(1024).decode()

print('Received', repr(data))

if data == "bye" or data == "arret":
    client_socket.close()
