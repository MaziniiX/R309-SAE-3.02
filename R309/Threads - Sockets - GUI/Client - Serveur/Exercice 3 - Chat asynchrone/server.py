import socket
import threading

host = '0.0.0.0'
port = 12345
flag = False

def handle_client(conn, address):
    while True:
        message = conn.recv(1024).decode()
        print("Received from {}: {}".format(address, message))

        if message.lower() == 'bye':
            reply = "Bye"
            conn.send(reply.encode())
            conn.close()
            break
        elif message.lower() == 'arret':
            print("Server shutting down.")
            reply = "Server down."
            conn.send(reply.encode())
            conn.close()
            server_socket.close()
            break
        else:
            reply = "Received: {}".format(message)
            conn.send(reply.encode())

server_socket = socket.socket()
server_socket.bind((host, port))
server_socket.listen(1)

print("Server listening on {}:{}".format(host, port))

while not flag:
    conn, address = server_socket.accept()
    print("Connection established with {}".format(address))

    client_thread = threading.Thread(target=handle_client, args=(conn, address))
    client_thread.start()

server_socket.close()
