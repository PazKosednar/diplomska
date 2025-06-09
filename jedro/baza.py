import sqlite3
import os

# Pot do baze
POT_DO_BAZE = os.path.join("podatki", "baza.db")

def povezava():
    return sqlite3.connect(POT_DO_BAZE)

def ustvari_bazo():
    povezava_baza = povezava()
    kazalec = povezava_baza.cursor()

    # Tabela zaposlenih
    kazalec.execute("""
        CREATE TABLE IF NOT EXISTS zaposleni (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ime TEXT NOT NULL,
            priimek TEXT NOT NULL,
            delovno_mesto TEXT,
            slika TEXT,
            face_encoding BLOB,
            pin TEXT
        )
    """)

    # Tabela prisotnosti
    kazalec.execute("""
        CREATE TABLE IF NOT EXISTS prisotnost (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zaposleni_id INTEGER,
            datum TEXT,
            ura_prihoda TEXT,
            ura_odhoda TEXT,
            FOREIGN KEY (zaposleni_id) REFERENCES zaposleni(id)
        )
    """)

    povezava_baza.commit()
    povezava_baza.close()

if __name__ == "__main__":
    # Če mapa 'podatki' ne obstaja, jo ustvari
    if not os.path.exists("podatki"):
        os.makedirs("podatki")

    ustvari_bazo()
    print("✅ Baza uspešno ustvarjena.")
