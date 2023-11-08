import socket

port = 65535

server_socket = socket.socket()
server_socket.bind(('127.0.0.1', port))
server_socket.listen(1)
while True:
    conn, address = server_socket.accept()
    with conn:
        print('Connected by', address)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.send(data)
        break
reply = "bye"