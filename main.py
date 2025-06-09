import sys
import os
import hashlib
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel,
    QInputDialog, QLineEdit, QMessageBox
)
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt
from jedro import baza
from vmesnik.dodaj_zaposlen import DodajZaposlenega
from vmesnik.prepoznava import Prepoznava
from vmesnik.pregled_prisotnosti import PregledPrisotnosti
from vmesnik.admin_okno import AdminOkno


class GlavnoOkno(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistem za beleženje prisotnosti")
        self.setFixedSize(500, 450)
        self.nastavi_vmesnik()
        self.admin_id = None

    def nastavi_vmesnik(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }

            QLabel {
                font-weight: bold;
                font-size: 18px;
                color: #ffffff;
            }

            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 10px 18px;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                font-size: 14px;
            }

            QPushButton:hover {
                background-color: #3d3d3d;
                border: 1px solid #5a5a5a;
            }

            QLineEdit, QComboBox {
                background-color: #292929;
                color: #ffffff;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 6px;
            }

            QLineEdit:focus {
                border: 1px solid #00bfff;
            }
        """)

        naslov = QLabel("📋 Sistem za beleženje prisotnosti")
        naslov.setFont(QFont("Segoe UI", 18))
        naslov.setAlignment(Qt.AlignCenter)
        naslov.setStyleSheet("margin-bottom: 30px;")

        gumb_prepoznaj = QPushButton("📷 Zaženi prepoznavo")
        gumb_prepoznaj.setMinimumHeight(40)
        gumb_prepoznaj.clicked.connect(self.odpri_prepoznavo)

        gumb_admin = QPushButton("🔒 Admin nadzor")
        gumb_admin.setMinimumHeight(40)
        gumb_admin.clicked.connect(self.odpri_admin)

        postavitev = QVBoxLayout()
        postavitev.setContentsMargins(40, 30, 40, 30)
        postavitev.setSpacing(20)
        postavitev.addWidget(naslov)
        postavitev.addWidget(gumb_prepoznaj)
        postavitev.addWidget(gumb_admin)

        self.setLayout(postavitev)

    def odpri_prepoznavo(self):
        self.okno_prepoznava = Prepoznava()
        self.okno_prepoznava.show()

    def odpri_pregled(self):
        self.okno_pregled = PregledPrisotnosti()
        self.okno_pregled.show()

    def odpri_admin(self):
        uporabnik, ok1 = QInputDialog.getText(self, "Admin prijava", "Uporabniško ime:")
        if not ok1 or not uporabnik:
            return

        geslo, ok2 = QInputDialog.getText(self, "Admin prijava", "Geslo (PIN):", QLineEdit.Password)
        if not ok2 or not geslo:
            return

        geslo_hash = hashlib.sha256(geslo.encode()).hexdigest()

        con = baza.povezava()
        cur = con.cursor()
        cur.execute("SELECT id, pin, admin FROM zaposleni WHERE username = ?", (uporabnik,))
        rezultat = cur.fetchone()
        con.close()

        if not rezultat:
            QMessageBox.warning(self, "Napaka", "Uporabniško ime ne obstaja.")
            return

        id_up, pin_iz_baze, admin_flag = rezultat

        if geslo_hash != pin_iz_baze:
            QMessageBox.warning(self, "Napaka", "Geslo ni pravilno.")
            return

        if admin_flag != 1:
            QMessageBox.warning(self, "Napaka", "Uporabnik nima administratorskih pravic.")
            return

        self.okno_admin = AdminOkno()
        self.okno_admin.show()


def zagon_aplikacije():
    if not os.path.exists("podatki"):
        os.makedirs("podatki")

    baza.ustvari_bazo()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Pomembno: omogoči Fusion stil

    # Nastavi temno paleto
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.WindowText, QColor(220, 220, 220))
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(35, 35, 35))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Text, QColor(220, 220, 220))
    dark_palette.setColor(QPalette.Button, QColor(45, 45, 45))
    dark_palette.setColor(QPalette.ButtonText, QColor(220, 220, 220))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))

    app.setPalette(dark_palette)

    okno = GlavnoOkno()
    okno.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    zagon_aplikacije()
