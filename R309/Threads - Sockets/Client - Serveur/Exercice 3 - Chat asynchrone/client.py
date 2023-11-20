"""
Ce programme est un client TCP simple qui se connecte à un serveur sur l'adresse IP '127.0.0.1' et le port 12345. Il reçoit des messages du serveur et envoie des messages à celui-ci.

Fonctions :
- receive_messages(client_socket) : Cette fonction est exécutée dans un thread séparé et reçoit constamment des messages du serveur. Si le message reçu est 'arret' ou 'bye', la connexion du client est fermée.

Variables :
- host : L'adresse IP du serveur auquel le client se connecte.
- port : Le port du serveur auquel le client se connecte.
- flag : Un drapeau pour indiquer si le client doit se déconnecter ou non.
- client_socket : Le socket client utilisé pour se connecter au serveur.
- receive_thread : Le thread utilisé pour recevoir des messages du serveur.

Le client envoie des messages au serveur jusqu'à ce que 'bye' ou 'arret' soit entré. Si 'bye' ou 'arret' est entré, le client se déconnecte.
"""

import socket
import threading

host = '127.0.0.1'
port = 12345
flag = False

def receive_messages(client_socket):
    while True:
        reply = client_socket.recv(1024).decode()
        print("Reply from server:", reply)
        if reply.lower() == 'arret' or reply.lower() == 'bye':
            print("Client disconnection.")
            client_socket.close()
            break

client_socket = socket.socket()
client_socket.connect((host, port))

receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
receive_thread.start()

while not flag:
    message = input("Write your message (leave with bye, close the server with arret): ")
    client_socket.send(message.encode())

    if message.lower() == 'bye' or message.lower() == 'arret':
        print("Client disconnection.")
        client_socket.close()
        flag = True

client_socket.close()
