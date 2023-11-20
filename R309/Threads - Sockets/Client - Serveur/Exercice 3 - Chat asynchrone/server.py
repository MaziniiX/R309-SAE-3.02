"""
Ce programme est un serveur de chat simple utilisant des sockets et du multithreading.

Il écoute les connexions entrantes sur le port spécifié et crée un nouveau thread pour chaque client connecté.
Chaque thread gère la réception des messages du client et envoie une réponse.

Fonctions :
- handle_client(conn, address) : Gère la connexion avec le client. Reçoit les messages du client et envoie une réponse. Si le message est 'bye', la connexion avec le client est fermée. Si le message est 'arret', le serveur est arrêté.
- receive_messages(conn, address) : Reçoit les messages du client et les affiche.

Variables :
- host : L'adresse IP sur laquelle le serveur est hébergé.
- port : Le port sur lequel le serveur écoute les connexions entrantes.
- flag : Un drapeau pour indiquer si le serveur doit être arrêté.
- server_socket : Le socket du serveur.
- conn : Le socket du client.
- address : L'adresse du client.
- client_thread : Le thread pour gérer la connexion avec le client.
- receive_thread : Le thread pour recevoir les messages du client.
"""

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
            global flag
            flag = True
            break
        else:
            reply = "Received: {}".format(message)
            conn.send(reply.encode())

def receive_messages(conn, address):
    while True:
        message = conn.recv(1024).decode()
        print("Received from {}: {}".format(address, message))

server_socket = socket.socket()
server_socket.bind((host, port))
server_socket.listen(1)

print("Server listening on {}:{}".format(host, port))

conn, address = server_socket.accept()
print("Connection established with {}".format(address))

client_thread = threading.Thread(target=handle_client, args=(conn, address))
client_thread.start()

receive_thread = threading.Thread(target=receive_messages, args=(conn, address))
receive_thread.start()

while not flag:
    message = input("Write your message (leave with bye, close the server with arret): ")
    conn.send(message.encode())

server_socket.close()
