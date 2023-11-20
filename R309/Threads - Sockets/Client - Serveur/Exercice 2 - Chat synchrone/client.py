"""
Ce programme est un client TCP simple qui se connecte à un serveur sur l'adresse IP locale (127.0.0.1) et le port 12345.

Il permet à l'utilisateur d'envoyer des messages au serveur. L'utilisateur peut quitter le programme en envoyant le message 'bye' ou fermer le serveur en envoyant le message 'arret'.

Après chaque message envoyé, le programme attend une réponse du serveur et l'affiche à l'utilisateur. Si la réponse du serveur est 'arret' ou si le message de l'utilisateur est 'bye', le programme se termine.

Fonctionnement :
1. Crée un socket client et se connecte au serveur.
2. Demande à l'utilisateur d'entrer un message.
3. Envoie le message au serveur.
4. Si le message est 'bye' ou 'arret', déconnecte le client et termine le programme.
5. Reçoit la réponse du serveur et l'affiche à l'utilisateur.
6. Si la réponse est 'arret' ou si le message de l'utilisateur est 'bye', déconnecte le client et termine le programme.
7. Ferme le socket client.
"""

import socket

host = '127.0.0.1'
port = 12345
flag = False

while not flag:
    client_socket = socket.socket()
    client_socket.connect((host, port))

    message = input("Write your message (leave with bye, close the server with arret): ")
    client_socket.send(message.encode())

    if message.lower() == 'bye' or message.lower() == 'arret':
        print("Client disconnection.")
        client_socket.close()
        flag = True

    reply = client_socket.recv(1024).decode()
    print("Reply from server :", reply)

    if reply.lower() == 'arret' or message.lower() == 'bye':
        print("Client disconnection")
        client_socket.close()
        flag = True

    client_socket.close()


