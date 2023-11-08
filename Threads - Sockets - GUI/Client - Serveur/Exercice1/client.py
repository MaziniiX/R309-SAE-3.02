import socket

port = 65535
host = '127.0.0.1'

try:
    client_socket = socket.socket()
    client_socket.connect((host, port))
    data = client_socket.recv(1024).decode()
    print("Received", repr(data))

except TimeoutError as err:
    print(err)
except ConnectionRefusedError as err:
    print(err)
except ConnectionResetError as err:
    print(err)
except socket.gaierror as err:
    print(err)
except BrokenPipeError as err:
    print(err)

else:
    if data == "bye":
        client_socket.close()