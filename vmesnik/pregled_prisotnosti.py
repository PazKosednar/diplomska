from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QDateEdit, QMessageBox, QFileDialog
)
from PyQt5.QtCore import QDate
from jedro.baza import povezava
import csv


class PregledPrisotnosti(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pregled prisotnosti")
        self.setMinimumSize(600, 400)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(5)
        self.tabela.setHorizontalHeaderLabels(["Ime", "Priimek", "Datum", "Prihod", "Odhod"])

        self.izberi_datum = QDateEdit(calendarPopup=True)
        self.izberi_datum.setDate(QDate.currentDate())

        self.gumb_osvezi = QPushButton("🔄 Osveži")
        self.gumb_izvoz = QPushButton("⬇️ Izvozi v CSV")
        self.gumb_izbrisi = QPushButton("🗑️ Izbriši izbrano prisotnost")

        self.gumb_osvezi.clicked.connect(self.prikazi_podatke)
        self.gumb_izvoz.clicked.connect(self.izvozi_csv)
        self.gumb_izbrisi.clicked.connect(self.izbrisi_izbrano)

        zgornja_vrstica = QHBoxLayout()
        zgornja_vrstica.addWidget(QLabel("Izberi datum:"))
        zgornja_vrstica.addWidget(self.izberi_datum)
        zgornja_vrstica.addWidget(self.gumb_osvezi)
        zgornja_vrstica.addWidget(self.gumb_izvoz)
        zgornja_vrstica.addWidget(self.gumb_izbrisi)

        glavna_postavitev = QVBoxLayout()
        glavna_postavitev.addLayout(zgornja_vrstica)
        glavna_postavitev.addWidget(self.tabela)

        self.setLayout(glavna_postavitev)
        self.prikazi_podatke()  # samodejno pokaži trenutni dan

    def prikazi_podatke(self):
        izbran_datum = self.izberi_datum.date().toString("yyyy-MM-dd")

        povezava_baza = povezava()
        kazalec = povezava_baza.cursor()

        kazalec.execute("""
            SELECT z.ime, z.priimek, p.datum, p.ura_prihoda, p.ura_odhoda
            FROM prisotnost p
            JOIN zaposleni z ON p.zaposleni_id = z.id
            WHERE p.datum = ?
            ORDER BY p.ura_prihoda
        """, (izbran_datum,))

        rezultati = kazalec.fetchall()
        self.tabela.setRowCount(len(rezultati))

        for vrstica, (ime, priimek, datum, prihod, odhod) in enumerate(rezultati):
            self.tabela.setItem(vrstica, 0, QTableWidgetItem(ime))
            self.tabela.setItem(vrstica, 1, QTableWidgetItem(priimek))
            self.tabela.setItem(vrstica, 2, QTableWidgetItem(datum))
            self.tabela.setItem(vrstica, 3, QTableWidgetItem(prihod or "-"))
            self.tabela.setItem(vrstica, 4, QTableWidgetItem(odhod or "-"))

        povezava_baza.close()

    def izvozi_csv(self):
        pot, _ = QFileDialog.getSaveFileName(self, "Shrani CSV", "", "CSV datoteke (*.csv)")
        if not pot:
            return

        vrstic = self.tabela.rowCount()
        stolpcev = self.tabela.columnCount()

        try:
            with open(pot, mode="w", newline="", encoding="utf-8") as dat:
                pisec = csv.writer(dat)
                glave = [self.tabela.horizontalHeaderItem(i).text() for i in range(stolpcev)]
                pisec.writerow(glave)

                for vrstica in range(vrstic):
                    vrst = []
                    for stolpec in range(stolpcev):
                        item = self.tabela.item(vrstica, stolpec)
                        vrst.append(item.text() if item else "")
                    pisec.writerow(vrst)
            QMessageBox.information(self, "Izvoz", "Podatki uspešno izvoženi.")
        except Exception as e:
            QMessageBox.critical(self, "Napaka", f"Napaka pri izvozu: {e}")

    def izbrisi_izbrano(self):
        izbrana_vrstica = self.tabela.currentRow()
        if izbrana_vrstica == -1:
            QMessageBox.warning(self, "Napaka", "Najprej izberi vrstico.")
            return

        ime = self.tabela.item(izbrana_vrstica, 0).text()
        priimek = self.tabela.item(izbrana_vrstica, 1).text()
        datum = self.tabela.item(izbrana_vrstica, 2).text()
        prihod = self.tabela.item(izbrana_vrstica, 3).text()

        odgovor = QMessageBox.question(
            self,
            "Potrditev brisanja",
            f"Ali želiš izbrisati prisotnost za {ime} {priimek} ({datum}, {prihod})?",
            QMessageBox.Yes | QMessageBox.No
        )

        if odgovor != QMessageBox.Yes:
            return

        con = povezava()
        cur = con.cursor()
        cur.execute("""
            DELETE FROM prisotnost
            WHERE datum = ? AND ura_prihoda = ?
              AND zaposleni_id = (
                  SELECT id FROM zaposleni WHERE ime = ? AND priimek = ?
              )
        """, (datum, prihod, ime, priimek))
        con.commit()
        con.close()

        self.prikazi_podatke()
        QMessageBox.information(self, "Uspeh", "Prisotnost izbrisana.")
