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
        lab = QLabel("Saisir votre nom")
        self.text = QLineEdit()
        ok = QPushButton("Ok")
        quit = QPushButton("Quitter")
        # Ajouter les composants au grid ayout
        self.grid.addWidget(lab, 0, 0, 1, 2)
        self.grid.addWidget(self.text, 1, 0, 1, 2)
        self.grid.addWidget(ok, 2, 0, 2, 2)
        self.grid.addWidget(quit, 4, 0, 2, 2)

        ok.clicked.connect(self.__actionOk)
        quit.clicked.connect(self.__actionQuitter)

        self.setWindowTitle("Exercice 1")
    def __actionOk(self):
        hello = QLabel(f"Bonjour " + self.text.text())
        self.grid.addWidget(hello, 3, 0, 1, 2)
    def __actionQuitter(self):
        QCoreApplication.exit(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(300, 200)
    window.show()
    app.exec()