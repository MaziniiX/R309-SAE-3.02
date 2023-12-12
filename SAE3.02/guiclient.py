import sys

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QPushButton, \
    QHBoxLayout, QListWidget, QStackedWidget, QTextBrowser, QLabel, QLineEdit, QMessageBox
import socket
import threading

class ChatWidget(QWidget):
    message_received = pyqtSignal(str)
    message_sent = pyqtSignal(str)

    def __init__(self, username, users_list_widget, messages_widget, private_messages_widget):
        super().__init__()

        self.username = username
        self.users_list_widget = users_list_widget
        self.messages_widget = messages_widget
        self.private_messages_widget = private_messages_widget

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.message_area = QTextBrowser()
        self.message_area.setReadOnly(True)

        self.input_area = QTextEdit()
        self.input_area.setPlaceholderText("Type your message here...")
        self.input_area.setMaximumHeight(100)

        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message)

        layout.addWidget(self.message_area)
        layout.addWidget(self.input_area)
        layout.addWidget(send_button)

        self.setLayout(layout)

    def send_message(self):
        message = self.input_area.toPlainText().strip()
        if message:
            self.message_sent.emit(message)
            self.input_area.clear()

    def display_message(self, sender, content):
        self.message_area.append(f"{sender}: {content}")

    def display_private_message(self, sender, content):
        self.private_messages_widget.append(f"{sender}: {content}")

class PrivateChatWindow(QWidget):
    def __init__(self, username, target_user):
        super().__init__()

        self.username = username
        self.target_user = target_user

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.private_messages_widget = QTextBrowser()
        self.private_messages_widget.setReadOnly(True)

        self.input_area = QTextEdit()
        self.input_area.setPlaceholderText("Type your message here...")
        self.input_area.setMaximumHeight(100)

        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_private_message)

        layout.addWidget(self.private_messages_widget)
        layout.addWidget(self.input_area)
        layout.addWidget(send_button)

        self.setLayout(layout)

    def send_private_message(self):
        message = self.input_area.toPlainText().strip()
        if message:
            # Here you can send the private message to the server
            # For now, let's print it to the console
            print(f"Private message sent to {self.target_user}: {message}")

            # Display the private message in the window
            self.private_messages_widget.append(f"{self.username}: {message}")

class ChatApp(QMainWindow):
    def __init__(self, username):
        super().__init__()

        self.username = username
        self.chat_client = login_signup_page  # Store reference to ChatClient instance
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        layout = QHBoxLayout()

        # Left Panel - Users Sidebar
        users_list_widget = QListWidget()
        users_list_widget.addItems(["User1", "User2", "User3"])  # Replace with actual users
        users_list_widget.clicked.connect(self.open_private_chat)

        # Center Panel - Stacked Widget for Public and Private Chats
        stacked_widget = QStackedWidget()

        public_chat_widget = ChatWidget(self.username, users_list_widget, QTextBrowser(), None)
        private_chat_widget = PrivateChatWindow(self.username, "TargetUser")  # Replace with the actual target user

        stacked_widget.addWidget(public_chat_widget)
        stacked_widget.addWidget(private_chat_widget)

        layout.addWidget(users_list_widget)
        layout.addWidget(stacked_widget)

        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)
        self.setWindowTitle(f"Chat App - {self.username}")

    def open_private_chat(self, item):
        target_user = item.text()
        print(f"Opening private chat with {target_user}")

        # Set the index of the Private Chat widget in the stacked widget
        self.centralWidget().layout().itemAt(1).widget().setCurrentIndex(1)

class LoginSignupPage(QMainWindow):
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
        self.edit_host.setText("127.0.0.1")
        self.edit_port.setText("12345")
        self.username = ""

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
            print(login_response)

        elif response != b"login_signup":
            QMessageBox.critical(self, 'Unexpected Server Response', 'Expected login_signup from server.')
            return

        if login_response == b"LOGIN_SUCCESS":
            # Capture and store the username
            self.username = username
            self.open_success_window('Login Successful')
            # Create and show the ChatApp window
            self.chat_app = ChatApp(self.username)
            self.chat_app.show()
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
        print(signup_response)

        if signup_response == b"SIGNUP_SUCCESS":
            # Capture and store the username
            self.username = username
            self.open_success_window('Signup Successful')
            # Create and show the ChatApp window
            self.chat_app = ChatApp(self.username)
            self.chat_app.show()
        else:
            self.open_error_window('Signup Failed', 'Username is already taken.')

    def open_chat_app(self, username):
        chat_app = ChatApp(username)
        chat_app.show()
        self.hide()

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

    # Example usage: replace 'JohnDoe' with the actual username
    login_signup_page = LoginSignupPage()
    chat_app = ChatApp(login_signup_page)  # Pass ChatClient instance to ChatApp
    login_signup_page.show()

    sys.exit(app.exec())