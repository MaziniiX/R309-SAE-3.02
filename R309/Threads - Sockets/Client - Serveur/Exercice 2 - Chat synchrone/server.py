"""
Ce programme est un serveur TCP simple qui écoute sur l'adresse IP '0.0.0.0' et le port 12345. Il accepte les connexions entrantes, reçoit les messages des clients et renvoie une réponse.

Fonctionnement :
- Le serveur est en écoute sur l'adresse IP '0.0.0.0' et le port 12345.
- Lorsqu'une connexion est établie, le serveur imprime l'adresse du client.
- Le serveur reçoit un message du client. Si le message est 'bye', le serveur renvoie 'Bye' et ferme la connexion avec le client.
- Si le message est 'arret', le serveur imprime 'Server shutting down.', renvoie 'Server down.' au client, ferme la connexion avec le client et arrête le serveur.
- Pour tout autre message, le serveur renvoie 'Received : {message}' où {message} est le message reçu du client.

Note :
- Le serveur ne gère qu'une seule connexion à la fois. Si un client est connecté, les autres clients doivent attendre que la connexion soit fermée avant de pouvoir se connecter.
- Le serveur continue de fonctionner jusqu'à ce qu'il reçoive le message 'arret'.
"""

import socket

host = '0.0.0.0'
port = 12345
flag = False

server_socket = socket.socket()
server_socket.bind((host, port))
server_socket.listen(1)

print("Server listening on {}:{}".format(host, port))

while not flag:
    conn, address = server_socket.accept()
    print("Connection established with {}".format(address))

    message = conn.recv(1024).decode()
    print("Received :", message)

    if message.lower() == 'bye':
        reply = "Bye"
        conn.send(reply.encode())
        conn.close()
    elif message.lower() == 'arret':
        print("Server shutting down.")
        reply = "Server down."
        conn.send(reply.encode())
        conn.close()
        server_socket.close()
        flag = True
    else:
        reply = "Received : {}".format(message)
        conn.send(reply.encode())

    conn.close()
