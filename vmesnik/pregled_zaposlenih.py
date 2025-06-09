from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox
from jedro.baza import povezava

class PregledZaposlenih(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pregled zaposlenih")
        self.setMinimumSize(600, 400)
        self.nastavi_vmesnik()

    def nastavi_vmesnik(self):
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(["Ime", "Priimek", "Delovno mesto", "Dejanje"])

        self.osvezi_podatke()

        layout = QVBoxLayout()
        layout.addWidget(self.tabela)
        self.setLayout(layout)

    def osvezi_podatke(self):
        self.tabela.setRowCount(0)

        con = povezava()
        cur = con.cursor()
        cur.execute("SELECT id, ime, priimek, delovno_mesto FROM zaposleni")
        podatki = cur.fetchall()

        for i, (id_zaposleni, ime, priimek, delovno_mesto) in enumerate(podatki):
            self.tabela.insertRow(i)
            self.tabela.setItem(i, 0, QTableWidgetItem(ime))
            self.tabela.setItem(i, 1, QTableWidgetItem(priimek))
            self.tabela.setItem(i, 2, QTableWidgetItem(delovno_mesto))

            gumb_izbrisi = QPushButton("🗑️ Izbriši")
            gumb_izbrisi.clicked.connect(lambda _, id=id_zaposleni: self.izbrisi_zaposlenega(id))
            layout = QHBoxLayout()
            layout.addWidget(gumb_izbrisi)
            layout.setContentsMargins(0, 0, 0, 0)
            container = QWidget()
            container.setLayout(layout)
            self.tabela.setCellWidget(i, 3, container)

        con.close()

    def izbrisi_zaposlenega(self, id_zaposleni):
        odgovor = QMessageBox.question(self, "Potrditev brisanja", "Ali res želiš izbrisati zaposlenega?", QMessageBox.Yes | QMessageBox.No)
        if odgovor == QMessageBox.Yes:
            con = povezava()
            cur = con.cursor()
            cur.execute("DELETE FROM zaposleni WHERE id = ?", (id_zaposleni,))
            con.commit()
            con.close()
            self.osvezi_podatke()
