import socket

host = '127.0.0.1'
port = 12345

client_socket = socket.socket()
client_socket.connect((host, port))

message = "Hi"
client_socket.send(message.encode())

reply = client_socket.recv(1024).decode()
print("Message from server:", reply)

client_socket.close()
