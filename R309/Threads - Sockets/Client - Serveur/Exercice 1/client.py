"""
Ce programme est un client TCP simple qui se connecte à un serveur sur l'adresse IP locale (127.0.0.1) et le port 12345.

Il envoie un message "Hi" au serveur et attend une réponse. La réponse du serveur est reçue et affichée à l'écran. Après cela, la connexion avec le serveur est fermée.

Attributs:
    host (str): L'adresse IP du serveur auquel le client se connecte.
    port (int): Le port du serveur auquel le client se connecte.
    client_socket (socket.socket): Le socket client utilisé pour se connecter au serveur.
    message (str): Le message envoyé au serveur.
    reply (str): La réponse reçue du serveur.

"""

import socket

host = '127.0.0.1'
port = 12345

client_socket = socket.socket()
client_socket.connect((host, port))

message = "Hi"
client_socket.send(message.encode())

reply = client_socket.recv(1024).decode()
print("Message from server:", reply)

client_socket.close()
