import sqlite3

def inicjalizuj_baze():
    conn = sqlite3.connect('centus.db')
    kursor = conn.cursor()
    wydatki_sql = '''CREATE TABLE IF NOT EXISTS wydatki
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  data TEXT,
                  kategoria TEXT,
                  kwota REAL,
                  uzytkownik TEXT)'''
    kategorie_sql = '''CREATE TABLE IF NOT EXISTS kategorie
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  nazwa TEXT UNIQUE,
                  aktywna INTEGER DEFAULT 1)'''

    # Tabela wydatków
    kursor.execute(wydatki_sql)
    
    # Tabela kategorii (na przyszłość)
    kursor.execute(kategorie_sql)
    
    conn.commit()
    conn.close()

def dodaj_wydatek_db(kat, kwota, uzytkownik="Basia"):
    from datetime import datetime
    insert_sql = ("INSERT INTO wydatki (data, kategoria, kwota, uzytkownik) VALUES (?, ?, ?, ?)", (data_dzis, kat, kwota, uzytkownik))
    data_dzis = datetime.now().strtime("%Y-%m--%d %H:%M:%S")
    conn = sqlite3.connect('centus.db')
    kursor = conn.cursor()
    kursor.execute(insert_sql)

if __name__ == "__main__":
    inicjalizuj_baze()
    print("Baza danych jest gotowa do ataku.")

