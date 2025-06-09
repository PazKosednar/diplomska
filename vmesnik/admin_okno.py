from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QPushButton
from vmesnik.dodaj_zaposlen import DodajZaposlenega
from vmesnik.pregled_prisotnosti import PregledPrisotnosti
from vmesnik.pregled_zaposlenih import PregledZaposlenih


class AdminOkno(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛠️ Admin nadzorna plošča")
        self.setMinimumSize(800, 600)

        # Enoten stil
        self.setStyleSheet("""
            QWidget {
                background-color: #2e2e2e;
                color: white;
                font-family: Segoe UI, sans-serif;
                font-size: 14px;
            }

            QTabWidget::pane {
                border: 1px solid #444;
                background-color: #3c3c3c;
            }

            QTabBar::tab {
                background: #3c3c3c;
                color: white;
                padding: 10px;
                border: 1px solid #555;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                min-width: 120px;
            }

            QTabBar::tab:selected {
                background: #2d89ef;
                color: white;
            }
        """)

        # Gumb za osvežitev
        self.gumb_osvezi = QPushButton("🔄 Osveži")
        self.gumb_osvezi.clicked.connect(self.osvezi_zavihke)

        # Zavihki
        self.zavihki = QTabWidget()
        self.nalozi_zavihke()

        # Glavna postavitev
        layout = QVBoxLayout()
        layout.addWidget(self.gumb_osvezi)
        layout.addWidget(self.zavihki)
        self.setLayout(layout)

    def nalozi_zavihke(self):
        self.zavihki.clear()
        self.zavihki.addTab(PregledZaposlenih(), "👥 Zaposleni")
        self.zavihki.addTab(DodajZaposlenega(), "➕ Dodaj")
        self.zavihki.addTab(PregledPrisotnosti(), "📅 Prisotnost")

    def osvezi_zavihke(self):
        self.nalozi_zavihke()
