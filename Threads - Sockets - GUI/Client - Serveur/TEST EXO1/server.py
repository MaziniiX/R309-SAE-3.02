import socket

HOST = '127.0.0.1'
PORT = 65432

server_socket = socket.socket()
server_socket.bind((HOST, PORT))
server_socket.listen()
while True:
    conn, addr = server_socket.accept()
    with conn:
        print('Connected by', addr)
        while True:
                data = conn.recv(1024).decode()
                if not data:
                    break
                reply = "arret"
                conn.send(reply.encode())

