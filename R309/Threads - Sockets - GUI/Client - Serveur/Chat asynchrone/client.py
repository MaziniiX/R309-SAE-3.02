import socket
import threading

HOST = '127.0.0.1'
PORT = 65432


if __name__ == '__main':
    try:
        client_socket = socket.socket()
        client_socket.connect((HOST, PORT))

    except ConnectionAbortedError as err:
        print(err)

    else:
        t1 = threading.Thread(target=reception, args=[1])
        t1.start()
