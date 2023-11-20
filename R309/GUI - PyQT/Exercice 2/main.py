"""
Ce programme est une application de conversion de température utilisant PyQt6. Il permet à l'utilisateur de convertir des températures entre les degrés Celsius (°C) et Kelvin (K).

Classes :
    MainWindow(QMainWindow) : Cette classe représente la fenêtre principale de l'application.

Méthodes :
    __init__() : Initialise la fenêtre principale.
    update_units() : Met à jour les unités de température en fonction du type de conversion sélectionné.
    perform_conversion() : Convertit la température en fonction du type de conversion sélectionné.
    show_help() : Affiche un message d'aide.
    show_error_message(message) : Affiche un message d'erreur.

Si ce fichier est exécuté en tant que script principal, il crée une instance de QApplication, une instance de MainWindow, affiche la fenêtre principale et exécute l'application.
"""

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

        self.lbl_temp = QLabel("Température")

        self.temp = QLineEdit("")

        self.temp_unit = QLabel("°C")

        self.convert = QPushButton("Convertir")

        self.switch_unit = QComboBox()
        self.switch_unit.addItem('°C -> K')
        self.switch_unit.addItem('K -> °C')

        self.lbl_conversion = QLabel("Conversion")

        self.conversion = QLineEdit("")

        self.conversion_unit = QLabel("K")

        self.help = QPushButton("?")

        self.grid.addWidget(self.lbl_temp, 0, 0)
        self.grid.addWidget(self.temp, 0, 1)
        self.grid.addWidget(self.temp_unit, 0, 2)
        self.grid.addWidget(self.convert, 1, 1)
        self.grid.addWidget(self.switch_unit, 1, 2, 1, 2)
        self.grid.addWidget(self.lbl_conversion, 2, 0)
        self.grid.addWidget(self.conversion, 2, 1)
        self.grid.addWidget(self.conversion_unit, 2, 2)
        self.grid.addWidget(self.help, 3, 4)

        self.setWindowTitle("Conversion de Température")

        self.switch_unit.currentIndexChanged.connect(self.update_units)
        self.convert.clicked.connect(self.perform_conversion)
        self.help.clicked.connect(self.show_help)

    def update_units(self):
        conversion_type = self.switch_unit.currentText()
        if conversion_type == '°C -> K':
            self.temp_unit.setText("°C")
            self.conversion_unit.setText("K")
        elif conversion_type == 'K -> °C':
            self.temp_unit.setText("K")
            self.conversion_unit.setText("°C")

    def perform_conversion(self):
        try:
            temperature = float(self.temp.text())
            if temperature < -273.15 and self.switch_unit.currentText() == '°C -> K':
                self.show_error_message("Temperature cannot be below -273.15 °C.")
                return
            if temperature < 0 and self.switch_unit.currentText() == 'K -> °C':
                self.show_error_message("Temperature cannot be below 0 K.")

            conversion_type = self.switch_unit.currentText()
            if conversion_type == '°C -> K':
                converted_temperature = temperature + 273.15
            elif conversion_type == 'K -> °C':
                converted_temperature = temperature - 273.15
            else:
                return

            self.conversion.setText(f"{converted_temperature:.2f}")
        except ValueError:
            self.show_error_message("Invalid input. Please enter a valid number for temperature.")

    def show_help(self):
        help_message = "This is a temperature conversion tool. Enter a temperature, select the conversion type, and click 'Convertir'."
        QMessageBox.information(self, "Help", help_message, QMessageBox.StandardButton.Ok)

    def show_error_message(self, message):
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Icon.Critical)
        error_box.setText(message)
        error_box.setWindowTitle("Error")
        error_box.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()