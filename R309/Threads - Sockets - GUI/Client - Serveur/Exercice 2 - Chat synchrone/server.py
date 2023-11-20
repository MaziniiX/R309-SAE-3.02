import socket

host = '0.0.0.0'
port = 12345
flag = False

server_socket = socket.socket()
server_socket.bind((host, port))
server_socket.listen(1)

print("Server listening on {}:{}".format(host, port))

while not flag:
    conn, address = server_socket.accept()
    print("Connection established with {}".format(address))

    message = conn.recv(1024).decode()
    print("Received :", message)

    if message.lower() == 'bye':
        reply = "Bye"
        conn.send(reply.encode())
        conn.close()
    elif message.lower() == 'arret':
        print("Server shutting down.")
        reply = "Server down."
        conn.send(reply.encode())
        conn.close()
        server_socket.close()
        flag = True
    else:
        reply = "Received : {}".format(message)
        conn.send(reply.encode())

    conn.close()
