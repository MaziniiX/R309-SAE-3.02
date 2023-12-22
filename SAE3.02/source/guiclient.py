import sys
import socket
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QPushButton,
    QHBoxLayout, QListWidget, QStackedWidget, QTextBrowser, QLabel, QLineEdit, QMessageBox
)

class ChatWidget(QWidget):
    """
    Widget for displaying and interacting with the public chat.

    Attributes:
    - `message_received`: Signal emitted when a message is received.
    - `message_sent`: Signal emitted when a message is sent.

    Methods:
    - `__init__(self, username, users_list_widget, messages_widget, private_messages_widget)`: Initializes the ChatWidget.
    - `init_ui(self)`: Initializes the user interface.
    - `send_message(self)`: Sends a public message.
    - `display_message(self, sender, content)`: Displays a public message.
    - `display_private_message(self, sender, content)`: Displays a private message.
    """

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
        """
        Initializes the user interface of the ChatWidget.
        """
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
        """
        Sends a public message.
        """
        message = self.input_area.toPlainText().strip()
        if message:
            self.message_sent.emit(message)
            self.input_area.clear()

    def display_message(self, sender, content):
        """
        Displays a public message.

        Parameters:
        - `sender`: The sender of the message.
        - `content`: The content of the message.
        """
        self.message_area.append(f"{sender}: {content}")

    def display_private_message(self, sender, content):
        """
        Displays a private message.

        Parameters:
        - `sender`: The sender of the private message.
        - `content`: The content of the private message.
        """
        self.private_messages_widget.append(f"{sender}: {content}")

class PrivateChatWindow(QWidget):
    """
    Widget for displaying and interacting with private messages.

    Methods:
    - `__init__(self, username, target_user)`: Initializes the PrivateChatWindow.
    - `init_ui(self)`: Initializes the user interface.
    - `send_private_message(self)`: Sends a private message.
    """

    def __init__(self, username, target_user):
        super().__init__()

        self.username = username
        self.target_user = target_user

        self.init_ui()

    def init_ui(self):
        """
        Initializes the user interface of the PrivateChatWindow.
        """
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
        """
        Sends a private message.
        """
        message = self.input_area.toPlainText().strip()
        if message:
            print(f"Private message sent to {self.target_user}: {message}")
            self.private_messages_widget.append(f"{self.username}: {message}")

class ChatApp(QMainWindow):
    """
    Main application window for the chat application.

    Methods:
    - `__init__(self, username, chat_client)`: Initializes the ChatApp.
    - `init_ui(self)`: Initializes the user interface.
    - `open_private_chat(self, item)`: Opens a private chat window.
    """

    def __init__(self, username, chat_client):
        super().__init__()

        self.username = username
        self.chat_client = chat_client
        self.init_ui()

    def init_ui(self):
        """
        Initializes the user interface of the ChatApp.
        """
        central_widget = QWidget()
        layout = QHBoxLayout()

        users_list_widget = QListWidget()
        users_list_widget.addItems(["User1", "User2", "User3"])
        users_list_widget.clicked.connect(self.open_private_chat)

        stacked_widget = QStackedWidget()

        public_chat_widget = ChatWidget(self.username, users_list_widget, QTextBrowser(), None)
        private_chat_widget = PrivateChatWindow(self.username, "TargetUser")

        stacked_widget.addWidget(public_chat_widget)
        stacked_widget.addWidget(private_chat_widget)

        layout.addWidget(users_list_widget)
        layout.addWidget(stacked_widget)

        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)
        self.setWindowTitle(f"Chat App - {self.username}")

    def open_private_chat(self, item):
        """
        Opens a private chat window.

        Parameters:
        - `item`: The item clicked in the user list.
        """
        target_user = item.text()
        print(f"Opening private chat with {target_user}")
        self.centralWidget().layout().itemAt(1).widget().setCurrentIndex(1)

class LoginSignupPage(QMainWindow):
    """
    Login and signup page for the chat client.

    Methods:
    - `__init__(self)`: Initializes the LoginSignupPage.
    - `login_clicked(self)`: Handles the login button click event.
    - `signup_clicked(self)`: Handles the signup button click event.
    - `get_input_values(self)`: Retrieves input values from the UI.
    - `send_login_request(self, username, password)`: Sends a login request to the server.
    - `send_signup_request(self, username, password)`: Sends a signup request to the server.
    - `open_chat_app(self)`: Opens the main chat application window.
    - `show_connection_error(self, error)`: Displays a connection error message.
    - `show_unexpected_response_error(self)`: Displays an unexpected server response error message.
    - `open_success_window(self, message)`: Displays a success message.
    - `open_error_window(self, title, message)`: Displays an error message.
    - `send_message(self, message)`: Sends a message to the server.
    - `receive_message(self)`: Receives a message from the server.
    """

    def __init__(self):
        super().__init__()

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

        self.button_login.clicked.connect(self.login_clicked)
        self.button_signup.clicked.connect(self.signup_clicked)

    def login_clicked(self):
        """
        Handles the login button click event.
        """
        host, port, username, password = self.get_input_values()

        try:
            self.client_socket.connect((host, port))
        except Exception as e:
            self.show_connection_error(e)
            return

        response = self.receive_message()

        if response == b"login_signup":
            self.send_login_request(username, password)
            login_response = self.receive_message()
            print(login_response)

            if login_response == b"LOGIN_SUCCESS":
                self.username = username
                self.open_success_window('Login Successful')
                self.open_chat_app()
            else:
                self.open_error_window('Login Failed', 'Invalid username or password.')
        else:
            self.show_unexpected_response_error()

    def signup_clicked(self):
        """
        Handles the signup button click event.
        """
        host, port, username, password = self.get_input_values()

        try:
            self.client_socket.connect((host, port))
        except Exception as e:
            self.show_connection_error(e)
            return

        response = self.receive_message()

        if response == b"login_signup":
            self.send_signup_request(username, password)
            signup_response = self.receive_message()
            print(signup_response)

            if signup_response == b"SIGNUP_SUCCESS":
                self.username = username
                self.open_success_window('Signup Successful')
                self.open_chat_app()
            else:
                self.open_error_window('Signup Failed', 'Username is already taken.')
        else:
            self.show_unexpected_response_error()

    def get_input_values(self):
        """
        Retrieves input values from the UI.

        Returns:
        - Tuple containing host, port, username, and password.
        """
        host = self.edit_host.text()
        port = int(self.edit_port.text())
        username = self.edit_username.text()
        password = self.edit_password.text()
        return host, port, username, password

    def send_login_request(self, username, password):
        """
        Sends a login request to the server.

        Parameters:
        - `username`: The username for login.
        - `password`: The password for login.
        """
        self.send_message(b"login")
        self.send_message(username.encode())
        self.send_message(password.encode())

    def send_signup_request(self, username, password):
        """
        Sends a signup request to the server.

        Parameters:
        - `username`: The username for signup.
        - `password`: The password for signup.
        """
        self.send_message(b"signup")
        self.send_message(username.encode())
        self.send_message(password.encode())

    def open_chat_app(self):
        """
        Opens the main chat application window.
        """
        self.chat_app = ChatApp(self.username, self)
        self.chat_app.show()

    def show_connection_error(self, error):
        """
        Displays a connection error message.

        Parameters:
        - `error`: The error message.
        """
        QMessageBox.critical(self, 'Connection Error', f'Failed to connect to the server: {error}')

    def show_unexpected_response_error(self):
        """
        Displays an unexpected server response error message.
        """
        QMessageBox.critical(self, 'Unexpected Server Response', 'Expected login_signup from server.')

    def open_success_window(self, message):
        """
        Displays a success message.

        Parameters:
        - `message`: The success message.
        """
        QMessageBox.information(self, 'Success', message)

    def open_error_window(self, title, message):
        """
        Displays an error message.

        Parameters:
        - `title`: The title of the error window.
        - `message`: The error message.
        """
        QMessageBox.critical(self, title, message)

    def send_message(self, message):
        """
        Sends a message to the server.

        Parameters:
        - `message`: The message to be sent.
        """
        message_bytes = message if isinstance(message, bytes) else message.encode()
        self.client_socket.sendall(message_bytes)

    def receive_message(self):
        """
        Receives a message from the server.

        Returns:
        - The received message.
        """
        return self.client_socket.recv(4096)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    login_signup_page = LoginSignupPage()
    login_signup_page.show()

    sys.exit(app.exec())