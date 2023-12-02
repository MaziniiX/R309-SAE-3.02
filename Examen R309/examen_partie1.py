import sys
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

        self.setWindowTitle("Chronomètre")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()