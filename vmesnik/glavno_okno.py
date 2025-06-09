from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QLabel
)
from PyQt5.QtGui import QFont

class GlavnoOkno(QWidget):
    def __init__(self):
        super().__init__()
        self.nastavi_okno()

    def nastavi_okno(self):
        self.setWindowTitle("Sistem za beleženje prisotnosti")
        self.setFixedSize(400, 300)

        # Naslov
        naslov = QLabel("Beleženje prisotnosti")
        naslov.setFont(QFont("Arial", 16))
        naslov.setStyleSheet("margin-bottom: 20px;")

        # Gumbi
        gumb_dodaj = QPushButton("➕ Dodaj zaposlenega")
        gumb_prepoznaj = QPushButton("📷 Zaženi prepoznavo")
        gumb_prisotnost = QPushButton("📅 Pregled prisotnosti")

        # Funkcije gumbov – zaenkrat samo izpis
        gumb_dodaj.clicked.connect(lambda: print("Dodaj zaposlenega"))
        gumb_prepoznaj.clicked.connect(lambda: print("Zaženi prepoznavo"))
        gumb_prisotnost.clicked.connect(lambda: print("Pregled prisotnosti"))

        # Postavitev
        postavitev = QVBoxLayout()
        postavitev.addWidget(naslov)
        postavitev.addWidget(gumb_dodaj)
        postavitev.addWidget(gumb_prepoznaj)
        postavitev.addWidget(gumb_prisotnost)

        self.setLayout(postavitev)
