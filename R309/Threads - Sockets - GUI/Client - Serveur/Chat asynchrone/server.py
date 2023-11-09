import socket
import threading

HOST = '127.0.0.1'
PORT = 65432

def reception():
    

if __name__ == '__main__':
    try:
        server_socket = socket.socket()
        server_socket.bind((HOST, PORT))
        server_socket.listen()

    except ConnectionAbortedError as err:
        print(err)

    else:
        t1 = threading.Thread(target=reception, args=[1])
        t1.start()