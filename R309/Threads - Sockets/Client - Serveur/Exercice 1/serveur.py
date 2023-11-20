"""
Ce programme est un serveur TCP/IP simple qui écoute les connexions entrantes sur le port 12345 et l'adresse IP 0.0.0.0.

Il utilise le module socket de Python pour créer un socket, le lier à l'adresse spécifiée, et écouter les connexions entrantes.

Une fois qu'une connexion est établie, le serveur reçoit un message du client, l'affiche, puis envoie une réponse au client avant de fermer la connexion.

Attributs:
    host (str): L'adresse IP sur laquelle le serveur écoute.
    port (int): Le port sur lequel le serveur écoute.
    server_socket (socket.socket): Le socket du serveur.
    conn (socket.socket): Le socket de la connexion client.
    address (str): L'adresse du client.
    message (str): Le message reçu du client.
    reply (str): La réponse envoyée au client.

"""

import socket

host = '0.0.0.0'
port = 12345

server_socket = socket.socket()
server_socket.bind((host, port))
server_socket.listen(1)

print("Server listening on {}:{}".format(host, port))

conn, address = server_socket.accept()
print("Connection established with {}".format(address))

message = conn.recv(1024).decode()
print("Received :", message)

reply = "Hi"
conn.send(reply.encode())

conn.close()
server_socket.close()
