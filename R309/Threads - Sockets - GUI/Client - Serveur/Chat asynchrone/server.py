import socket
import threading

HOST = '127.0.0.1'
PORT = 2222
class Arret(Exception):
    pass
def reception():
    while True:
        message = conn.recv(1024).decode
        print('\t'+ str(message))
        if message == "arret":
            raise Arret
    

if __name__ == '__main__':
    try:
        server_socket = socket.socket()
        server_socket.bind((HOST, PORT))
        server_socket.listen()


    except Arret:
        print("Arret")
        exit()

    else:
        conn, address = server_socket.accept()
        reply = str(input("Message :"))
        conn.send(reply.encode)
        t1 = threading.Thread(target=reception, args=[1])
        t1.start()

        if reply == "arret":
            raise Arret