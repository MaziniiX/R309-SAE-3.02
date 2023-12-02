import sys
import time
import threading
import socket
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        widget = QWidget()
        self.setCentralWidget(widget)
        self.grid = QGridLayout()
        widget.setLayout(self.grid)

        self.lbl_compteur = QLabel("Compteur :")
        self.compteur = QLineEdit("0")
        self.start_btn = QPushButton("Start")
        self.reset_btn = QPushButton("Reset")
        self.stop_btn = QPushButton("Stop")
        self.connect_btn = QPushButton("Connect")
        self.quit_btn = QPushButton("Quitter")

        self.grid.addWidget(self.lbl_compteur, 0, 0, 1, 1)
        self.grid.addWidget(self.compteur, 1, 0, 1, 2)
        self.grid.addWidget(self.start_btn, 2, 0, 1, 2)
        self.grid.addWidget(self.reset_btn, 3, 0, 1, 1)
        self.grid.addWidget(self.stop_btn, 3, 1, 1, 1)
        self.grid.addWidget(self.connect_btn, 4, 0, 1, 1)
        self.grid.addWidget(self.quit_btn, 4, 1, 1, 1)
        
        self.compteur.setDisabled(True)
        self.arret_thread = False

        self.setWindowTitle("Chronomètre")

        self.start_btn.clicked.connect(self.start)
        self.reset_btn.clicked.connect(self.reset)
        self.quit_btn.clicked.connect(self.quitter)
        self.stop_btn.clicked.connect(self.stop)
        self.connect_btn.clicked.connect(self.connect)



    def __start(self):
        try:
            self.arret_thread = False
            while not self.arret_thread:
                self.temps = int(self.compteur.text())
                self.temps += 1
                self.compteur.setText(f"{self.temps}")
                message = (f"{self.temps}")
                self.client_socket.send(message.encode())
                time.sleep(1)
        finally:
            pass

    def start(self):
        try:
            self.start_thread = threading.Thread(target=self.__start, args=())
            self.start_thread.start()
        finally:
            pass

    def reset(self):
        try:
            message = "Reset"
            self.client_socket.send(message.encode())
            self.compteur.setText("0")
        finally:
            pass

    def quitter(self):
        try:
            message = "Bye"
            self.client_socket.send(message.encode())
            self.stop()
            QCoreApplication.exit(0)
        finally:
            pass

    def stop(self):
        try:
            message = "Stop"
            self.client_socket.send(message.encode())
            self.arret_thread = True
        finally:
            pass

    def connect(self):
        try:
            self.client_socket = socket.socket()
            self.client_socket.connect(("127.0.0.1", 10000))
        except socket.error as err:
            print(f"Connection failed: {err}")
            exit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
