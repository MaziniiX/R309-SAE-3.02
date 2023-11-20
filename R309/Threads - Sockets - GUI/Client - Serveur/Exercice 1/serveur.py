import socket

host = '0.0.0.0'
port = 12345

server_socket = socket.socket()
server_socket.bind((host, port))
server_socket.listen(1)

print("Server listening on {}:{}".format(host, port))

conn, address = server_socket.accept()
print("Connection established with {}".format(address))

message = conn.recv(1024).decode()
print("Received :", message)

reply = "Hi"
conn.send(reply.encode())

conn.close()
server_socket.close()
