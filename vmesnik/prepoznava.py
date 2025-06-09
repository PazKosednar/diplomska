from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy, QSpacerItem
from PyQt5.QtCore import QTimer, Qt, QRect
from PyQt5.QtGui import QPixmap, QFont, QPainter, QPainterPath, QColor, QPen, QImage
import cv2, numpy as np, os
from jedro.baza import povezava
import face_recognition
from datetime import datetime, timedelta

class ZaznanUporabnikWidget(QWidget):
    def __init__(self, ime, priimek, id_up, delovno_mesto, pot_slike, status):
        super().__init__()
        self.setStyleSheet("""
            QWidget {
                background-color: #21252b;
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
            }
            QFrame#mainCard {
                background-color: #ffffff;
                border-radius: 20px;
            }
            QFrame#headerSection {
                background-color: #f5f5f5;
                border-radius: 20px;
                padding: 15px;
            }
            QLabel#nameLabel {
                color: #ffffff;
                font-weight: bold;
                font-size: 18px;
            }
            QLabel#infoLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QLabel#statusPrihod {
                color: #ffffff;
                font-weight: bold;
                font-size: 15px;
            }
            QLabel#statusOdhod {
                color: #ffffff;
                font-weight: bold;
                font-size: 15px;
            }
            QLabel#avatarPlaceholder {
                background-color: #37474F;
                color: white;
                border-radius: 40px;
                font-size: 22px;
                font-weight: bold;
            }
        """)

        main_card = QFrame()
        main_card.setObjectName("mainCard")
        main_card.setFixedWidth(280)
        main_card.setFixedHeight(360)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignCenter)

        card_layout = QVBoxLayout(main_card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        header_section = QFrame()
        header_section.setObjectName("headerSection")
        header_section.setMinimumHeight(130)
        header_layout = QVBoxLayout(header_section)
        header_layout.setAlignment(Qt.AlignCenter)

        # Avatar
        avatar_size = 80
        if pot_slike and os.path.exists(pot_slike):
            avatar_widget = QLabel()
            original = QPixmap(pot_slike).scaled(avatar_size, avatar_size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

            # Krožna maska
            rounded = QPixmap(avatar_size, avatar_size)
            rounded.fill(Qt.transparent)
            painter = QPainter(rounded)
            painter.setRenderHint(QPainter.Antialiasing)
            path = QPainterPath()
            path.addEllipse(0, 0, avatar_size, avatar_size)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, original)
            painter.end()

            # Avatar z robom
            border_pixmap = QPixmap(avatar_size + 6, avatar_size + 6)
            border_pixmap.fill(Qt.transparent)
            painter = QPainter(border_pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QColor("#ffffff"))
            painter.setPen(QPen(QColor("#4f9cc9"), 2))
            painter.drawEllipse(3, 3, avatar_size, avatar_size)
            painter.drawPixmap(3, 3, rounded)
            painter.end()

            avatar_widget.setPixmap(border_pixmap)
            avatar_widget.setAlignment(Qt.AlignCenter)
        else:
            avatar_widget = QLabel(ime[0].upper() + priimek[0].upper())
            avatar_widget.setObjectName("avatarPlaceholder")
            avatar_widget.setFixedSize(80, 80)
            avatar_widget.setAlignment(Qt.AlignCenter)

        header_layout.addWidget(avatar_widget)

        # Content
        content_section = QFrame()
        content_layout = QVBoxLayout(content_section)
        content_layout.setAlignment(Qt.AlignTop)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        # Ime
        ime_label = QLabel(f"{ime} {priimek}")
        ime_label.setObjectName("nameLabel")
        ime_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(ime_label)

        # Ločilna črta
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #e0e0e0;")
        content_layout.addWidget(separator)

        # ID
        id_label = QLabel(f"ID: {id_up}")
        id_label.setObjectName("infoLabel")
        id_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(id_label)

        # Pozicija
        pozicija_label = QLabel(f"Pozicija: {delovno_mesto}")
        pozicija_label.setObjectName("infoLabel")
        pozicija_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(pozicija_label)

        # Razmik
        content_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Status
        status_label = QLabel(f"Status: {status}")
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setObjectName("statusPrihod" if status == "Prihod" else "statusOdhod")
        content_layout.addWidget(status_label)

        # Sestavi kartico
        card_layout.addWidget(header_section)
        card_layout.addWidget(content_section)
        main_layout.addWidget(main_card, 0, Qt.AlignCenter)

class Prepoznava(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Live prepoznavanje")
        self.setFixedSize(1000, 500)

        self.kamera = cv2.VideoCapture(0)
        self.znani_encodings, self.podatki_uporabnikov = self.nalozi_podatke()

        self.label_slika = QLabel()
        self.label_slika.setFixedSize(640, 480)

        self.desni_panel = QVBoxLayout()
        self.desni_panel_widget = QWidget()
        self.desni_panel_widget.setLayout(self.desni_panel)

        layout = QHBoxLayout()
        layout.addWidget(self.label_slika)
        layout.addWidget(self.desni_panel_widget)
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.posodobi_frame)
        self.timer.start(10)

        self.prepoznani_id = {}
        self.prikazani_timerji = {}

    def nalozi_podatke(self):
        con = povezava()
        cur = con.cursor()
        cur.execute("SELECT id, ime, priimek, face_encoding, delovno_mesto, slika FROM zaposleni")
        podatki = cur.fetchall()
        con.close()

        encodings = []
        podatki_up = []
        for id_, ime, priimek, enc, dm, slika in podatki:
            np_enc = np.frombuffer(enc, dtype=np.float64)
            encodings.append(np_enc)
            podatki_up.append((id_, ime, priimek, dm, slika))
        return encodings, podatki_up

    def posodobi_frame(self):
        ret, frame = self.kamera.read()
        if not ret:
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        lokacije = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, lokacije)

        for (top, right, bottom, left), en in zip(lokacije, encodings):
            razdalje = face_recognition.face_distance(self.znani_encodings, en)
            indeks = np.argmin(razdalje)
            if razdalje[indeks] < 0.5:
                id_zap, ime, priimek, delovno_mesto, ime_slike = self.podatki_uporabnikov[indeks]
                self.oznaci_okvir(frame, ime + " " + priimek, (0, 255, 0), top, right, bottom, left)
                zadnji_cas = self.prepoznani_id.get(id_zap)
                zdaj = datetime.now()
                if not zadnji_cas or (zdaj - zadnji_cas) > timedelta(hours=1):
                    status = self.zabelezi_prisotnost(id_zap, ime, priimek)
                    self.prikazi_zaznan_status(id_zap, ime, priimek, delovno_mesto, status)
                    self.prepoznani_id[id_zap] = zdaj
            else:
                self.oznaci_okvir(frame, "Neznano", (0, 0, 255), top, right, bottom, left)

        img = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_BGR888)
        self.label_slika.setPixmap(QPixmap.fromImage(img))

    def oznaci_okvir(self, frame, ime, barva, top, right, bottom, left):
        cv2.rectangle(frame, (left, top), (right, bottom), barva, 2)
        cv2.putText(frame, ime, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, barva, 2)

    def zabelezi_prisotnost(self, id_osebe, ime, priimek):
        zdaj = datetime.now()
        datum = zdaj.strftime("%Y-%m-%d")
        ura = zdaj.strftime("%H:%M:%S")

        con = povezava()
        cur = con.cursor()
        cur.execute("SELECT id, ura_prihoda, ura_odhoda FROM prisotnost WHERE zaposleni_id = ? AND datum = ? ORDER BY id DESC LIMIT 1", (id_osebe, datum))
        zadnji = cur.fetchone()

        if not zadnji or zadnji[2]:
            cur.execute("INSERT INTO prisotnost (zaposleni_id, datum, ura_prihoda) VALUES (?, ?, ?)", (id_osebe, datum, ura))
            status = "Prihod"
        else:
            cur.execute("UPDATE prisotnost SET ura_odhoda = ? WHERE id = ?", (ura, zadnji[0]))
            status = "Odhod"

        con.commit()
        con.close()
        return status

    def prikazi_zaznan_status(self, id_up, ime, priimek, delovno_mesto, status):
        for i in reversed(range(self.desni_panel.count())):
            self.desni_panel.itemAt(i).widget().deleteLater()

        zaznan_label = QLabel("✔️ Zaznan")
        zaznan_label.setAlignment(Qt.AlignCenter)
        zaznan_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        zaznan_label.setStyleSheet("color: lime; background-color: #1e1e1e; padding: 20px; border-radius: 10px;")

        self.desni_panel.addWidget(zaznan_label)
        QTimer.singleShot(5000, lambda: self.prikazi_uporabnika(id_up, ime, priimek, delovno_mesto, status))

    def prikazi_uporabnika(self, id_up, ime, priimek, delovno_mesto, status):
        for i in reversed(range(self.desni_panel.count())):
            self.desni_panel.itemAt(i).widget().deleteLater()

        # Poiščemo pot do slike iz seznama uporabnikov
        ime_slike = ""
        for uporabnik in self.podatki_uporabnikov:
            if uporabnik[0] == id_up:
                ime_slike = uporabnik[4]  # slika
                break

        pot_slike = os.path.join("podatki", "slike", ime_slike) if ime_slike else ""

        print("Slika:", pot_slike, "obstaja:", os.path.exists(pot_slike))

        widget = ZaznanUporabnikWidget(ime, priimek, id_up, delovno_mesto, pot_slike, status)
        self.desni_panel.addWidget(widget)

        if id_up in self.prikazani_timerji:
            self.prikazani_timerji[id_up].stop()

        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(lambda: self.počisti_prikaz(id_up))
        timer.start(20000)
        self.prikazani_timerji[id_up] = timer

    def počisti_prikaz(self, id_up):
        for i in reversed(range(self.desni_panel.count())):
            self.desni_panel.itemAt(i).widget().deleteLater()
        self.prikazani_timerji.pop(id_up, None)
