import socket

HOST = '127.0.0.1'
PORT = 65432

if __name__ == '__main__':
    try:
        server_socket = socket.socket()
        server_socket.bind((HOST, PORT))
        server_socket.listen()

    except ConnectionAbortedError as err:
        print(err)

    else:
        reply = "arret"
        while True:
            conn, addr = server_socket.accept()
            with conn:
                print('Connected by', addr)
                while True:
                        data = conn.recv(1024).decode()
                        if not data:
                            break
                        conn.send(reply.encode())
            if reply == "arret":
                break

