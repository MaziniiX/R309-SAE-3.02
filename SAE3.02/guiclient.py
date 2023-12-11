import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox
from PyQt6.QtCore import Qt
import socket
import threading

class ChatClient(QMainWindow):
    def __init__(self):
        super().__init__()

        # UI setup
        self.setWindowTitle("Chat Client")
        self.setGeometry(100, 100, 400, 200)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.label_host = QLabel("Host:")
        self.edit_host = QLineEdit(self)
        self.layout.addWidget(self.label_host)
        self.layout.addWidget(self.edit_host)

        self.label_port = QLabel("Port:")
        self.edit_port = QLineEdit(self)
        self.layout.addWidget(self.label_port)
        self.layout.addWidget(self.edit_port)

        self.label_username = QLabel("Username:")
        self.edit_username = QLineEdit(self)
        self.layout.addWidget(self.label_username)
        self.layout.addWidget(self.edit_username)

        self.label_password = QLabel("Password:")
        self.edit_password = QLineEdit(self)
        self.edit_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.label_password)
        self.layout.addWidget(self.edit_password)

        self.button_login = QPushButton("Login", self)
        self.button_signup = QPushButton("Signup", self)
        self.layout.addWidget(self.button_login)
        self.layout.addWidget(self.button_signup)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect signals to slots
        self.button_login.clicked.connect(self.login_clicked)
        self.button_signup.clicked.connect(self.signup_clicked)

    def login_clicked(self):
        host = self.edit_host.text()
        port = int(self.edit_port.text())
        username = self.edit_username.text()
        password = self.edit_password.text()

        try:
            # Connect to the host with port
            self.client_socket.connect((host, port))
        except Exception as e:
            QMessageBox.critical(self, 'Connection Error', f'Failed to connect to the server: {e}')
            return

        # Wait for server to ask for login or signup
        response = self.receive_message()

        if response == b"login_signup":
            # Send login request
            self.send_message(b"login")

            # Send username
            self.send_message(username.encode())

            # Send password
            self.send_message(password.encode())

            # Wait for server response
            login_response = self.receive_message()

        elif response != b"login_signup":
            QMessageBox.critical(self, 'Unexpected Server Response', 'Expected login_signup from server.')
            return

        if login_response == b"LOGIN_SUCCESS":
            self.open_success_window('Login Successful')
        else:
            self.open_error_window('Login Failed', 'Invalid username or password.')

    def signup_clicked(self):
        host = self.edit_host.text()
        port = int(self.edit_port.text())
        username = self.edit_username.text()
        password = self.edit_password.text()

        try:
            # Connect to the host with port
            self.client_socket.connect((host, port))
        except Exception as e:
            QMessageBox.critical(self, 'Connection Error', f'Failed to connect to the server: {e}')
            return

        # Wait for server to ask for login or signup
        response = self.receive_message()

        if response != b"login_signup":
            QMessageBox.critical(self, 'Unexpected Server Response', 'Expected login_signup from server.')
            return

        # Send signup request
        self.send_message(b"signup")

        # Send username
        self.send_message(username.encode())

        # Send password
        self.send_message(password.encode())

        # Wait for server response
        signup_response = self.receive_message()

        if signup_response == b"SIGNUP_SUCCESS":
            self.open_success_window('Signup Successful')
        else:
            self.open_error_window('Signup Failed', 'Username is already taken.')

    def open_success_window(self, message):
        QMessageBox.information(self, 'Success', message)

    def open_error_window(self, title, message):
        QMessageBox.critical(self, title, message)

    def send_message(self, message):
        message_bytes = message if isinstance(message, bytes) else message.encode()
        self.client_socket.sendall(message_bytes)

    def receive_message(self):
        return self.client_socket.recv(4096)  # Adjust the buffer size as needed

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = ChatClient()
    client.show()
    sys.exit(app.exec())
