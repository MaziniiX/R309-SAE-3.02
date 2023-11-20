"""
Ce programme crée une interface graphique simple avec PyQt6. 

Classes:
    MainWindow: Une classe pour représenter la fenêtre principale de l'application.

Méthodes:
    __init__ : Initialise la fenêtre principale.
    __actionOk : Affiche un message de bienvenue avec le nom saisi par l'utilisateur.
    __actionQuitter : Ferme l'application.

L'application demande à l'utilisateur de saisir son nom, puis affiche un message de bienvenue avec le nom saisi. L'utilisateur peut également quitter l'application en appuyant sur le bouton "Quitter".
"""

import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

class MainWindow(QMainWindow):
    """
    Une classe utilisée pour représenter la fenêtre principale de l'application

    ...

    Attributs
    ----------
    grid : QGridLayout
        un layout pour organiser les widgets dans la fenêtre
    text : QLineEdit
        un champ de texte pour saisir le nom de l'utilisateur

    Méthodes
    -------
    __actionOk():
        Affiche un message de bienvenue avec le nom saisi par l'utilisateur.
    __actionQuitter():
        Ferme l'application.
    """
    def __init__(self):
        """
        Initialise la fenêtre principale avec un QLabel, QLineEdit et deux QPushButton.
        """
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
        """
        Affiche un QLabel avec un message de bienvenue contenant le nom saisi par l'utilisateur.
        """
        hello = QLabel(f"Bonjour " + self.text.text())
        self.grid.addWidget(hello, 3, 0, 1, 2)
    def __actionQuitter(self):
        """
        Ferme l'application.
        """
        QCoreApplication.exit(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(300, 200)
    window.show()
    app.exec()
