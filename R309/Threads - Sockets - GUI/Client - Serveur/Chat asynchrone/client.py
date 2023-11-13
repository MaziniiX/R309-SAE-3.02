import socket
import threading

HOST = '127.0.0.1'
PORT = 2222
class Arret(Exception):
    pass

class Bye(Exception):
    pass

def reception():
    while True:
        message = client_socket.recv(1024).decode
        print('\t'+ str(message))
        if message == "arret":
            raise Arret
        if message == "bye":
            raise Bye

if __name__ == '__main__':
    try:
        client_socket = socket.socket()
        client_socket.connect((HOST, PORT))


    except Arret:
        print("Arret")
        client_socket.close()
        exit()

    except Bye:
        print("Bye")
        client_socket.close()
        exit()

    else:
        t1 = threading.Thread(target=reception)
        t1.start()
        message = str(input("Message :"))
        client_socket.send(message.encode())

