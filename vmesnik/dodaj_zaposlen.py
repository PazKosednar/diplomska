from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QCheckBox
)
from PyQt5.QtGui import QFont
import os
import cv2
import face_recognition
import numpy as np
import hashlib
import unidecode
from jedro.baza import povezava

MAPA_SLIK = os.path.join("podatki", "slike")
if not os.path.exists(MAPA_SLIK):
    os.makedirs(MAPA_SLIK)


class DodajZaposlenega(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dodaj zaposlenega")
        self.setFixedSize(400, 400)
        self.nastavi_vmesnik()

    def nastavi_vmesnik(self):
        self.vnos_ime = QLineEdit()
        self.vnos_priimek = QLineEdit()
        self.vnos_delovno_mesto = QLineEdit()

        self.vnos_pin = QLineEdit()
        self.vnos_pin.setEchoMode(QLineEdit.Password)

        self.vnos_pin_potrditev = QLineEdit()
        self.vnos_pin_potrditev.setEchoMode(QLineEdit.Password)

        self.oznaka_admin = QCheckBox("Admin uporabnik")
        self.vnos_uporabnisko_ime = QLineEdit()

        gumb_zajem = QPushButton("📸 Zajemi sliko in shrani")
        gumb_zajem.clicked.connect(self.zajemi_in_shrani)

        postavitev = QVBoxLayout()
        postavitev.addWidget(QLabel("Ime:"))
        postavitev.addWidget(self.vnos_ime)

        postavitev.addWidget(QLabel("Priimek:"))
        postavitev.addWidget(self.vnos_priimek)

        postavitev.addWidget(QLabel("Delovno mesto:"))
        postavitev.addWidget(self.vnos_delovno_mesto)

        postavitev.addWidget(QLabel("PIN:"))
        postavitev.addWidget(self.vnos_pin)

        postavitev.addWidget(QLabel("Potrdi PIN:"))
        postavitev.addWidget(self.vnos_pin_potrditev)

        postavitev.addWidget(self.oznaka_admin)

        postavitev.addWidget(QLabel("Uporabniško ime (za admina):"))
        postavitev.addWidget(self.vnos_uporabnisko_ime)

        postavitev.addWidget(gumb_zajem)

        self.setLayout(postavitev)

    def zajemi_in_shrani(self):
        ime = self.vnos_ime.text()
        priimek = self.vnos_priimek.text()
        delovno_mesto = self.vnos_delovno_mesto.text()
        pin = self.vnos_pin.text()
        pin_potrditev = self.vnos_pin_potrditev.text()
        je_admin = 1 if self.oznaka_admin.isChecked() else 0
        uporabnisko_ime = self.vnos_uporabnisko_ime.text()

        # Validacija
        if not (ime and priimek and pin):
            QMessageBox.warning(self, "Napaka", "Izpolni vsaj ime, priimek in PIN!")
            return

        if not pin.isdigit() or len(pin) != 4:
            QMessageBox.warning(self, "Napaka", "PIN mora biti 4-mestna številka!")
            return

        if pin != pin_potrditev:
            QMessageBox.warning(self, "Napaka", "PIN in potrditev PIN-a se ne ujemata!")
            return

        if je_admin and not uporabnisko_ime:
            QMessageBox.warning(self, "Napaka", "Admin mora imeti uporabniško ime.")
            return

        # Hash PIN
        pin_hash = hashlib.sha256(pin.encode()).hexdigest()

        # Kamera in zajem slike
        kamera = cv2.VideoCapture(0)
        if not kamera.isOpened():
            QMessageBox.critical(self, "Napaka", "Kamera ni na voljo.")
            return

        QMessageBox.information(self, "Navodilo", "Pritisni 'q' za zajem slike.")

        slika = None
        while True:
            ret, frame = kamera.read()
            if not ret:
                continue
            cv2.imshow("Zajem slike", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                slika = frame
                break

        kamera.release()
        cv2.destroyAllWindows()

        # Prepoznava obraza
        rgb_slika = cv2.cvtColor(slika, cv2.COLOR_BGR2RGB)
        obrazi = face_recognition.face_locations(rgb_slika)
        kodiranja = face_recognition.face_encodings(rgb_slika, obrazi)

        if not kodiranja:
            QMessageBox.warning(self, "Napaka", "Na sliki ni zaznan obraz.")
            return

        encoding = kodiranja[0]
        ime_datoteke = f"{unidecode.unidecode(ime)}_{unidecode.unidecode(priimek)}.jpg"
        pot_slike = os.path.join(MAPA_SLIK, ime_datoteke)
        cv2.imwrite(pot_slike, slika)

        # Shrani v bazo
        povezava_baza = povezava()
        kazalec = povezava_baza.cursor()
        kazalec.execute("""
            INSERT INTO zaposleni (ime, priimek, delovno_mesto, slika, face_encoding, pin, admin, username)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ime,
            priimek,
            delovno_mesto,
            ime_datoteke,
            encoding.tobytes(),
            pin_hash,
            je_admin,
            uporabnisko_ime
        ))

        povezava_baza.commit()
        povezava_baza.close()

        QMessageBox.information(self, "Uspeh", "Zaposleni uspešno dodan.")
        self.close()
