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


def dodaj_poczatkowe_kategorie_db():
    poczatkowe = ['Żywność', 'Dom', 'Auto', 'Odzież', 'Materiały do pracy', 'Podróże', 'Inne']
    conn = sqlite3.connect('centus.db')
    kursor = conn.cursor()
    # INSERT OR IGNORE sprawi, że nie zdublujemy wpisów przy każdym starcie
    kursor.executemany("INSERT OR IGNORE INTO kategorie (nazwa) VALUES (?)", 
                  [(k,) for k in poczatkowe])
    conn.commit()
    conn.close()

def pobierz_kategorie_db():
    conn = sqlite3.connect('centus.db')
    kursor = conn.cursor()
    # Pobieramy tylko aktywne kategorie
    kursor.execute("SELECT nazwa FROM kategorie WHERE aktywna = 1 ORDER BY nazwa ASC")
    wyniki = kursor.fetchall()
    conn.close()
    # Wynik z bazy to lista krotek [('Auto',), ('Dom',)], zamieniamy na prostą listę:
    return [k[0] for k in wyniki]

def dodaj_wydatek_db(kat, kwota, uzytkownik="Basia"):
    from datetime import datetime
    data_dzis = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect('centus.db')
    c = conn.cursor()
    c.execute("INSERT INTO wydatki (data, kategoria, kwota, uzytkownik) VALUES (?, ?, ?, ?)",
              (data_dzis, kat, kwota, uzytkownik))
    conn.commit()
    conn.close()

def pobierz_wydatki_miesieczne(rok, miesiac):
    import sqlite3
    conn = sqlite3.connect('centus.db')
    c = conn.cursor()
    
    # Wybieramy dzień i sumę wydatków dla danego miesiąca i roku
    # Używamy strftime, aby wyciągnąć dzień z formatu YYYY-MM-DD
    query = """
        SELECT strftime('%d', data) as dzien, SUM(kwota) 
        FROM wydatki 
        WHERE strftime('%Y', data) = ? AND strftime('%m', data) = ?
        GROUP BY dzien
    """
    # SQLite potrzebuje miesiąca w formacie "04" a nie "4"
    m_str = str(miesiac).zfill(2)
    c.execute(query, (str(rok), m_str))
    wyniki = c.fetchall()
    conn.close()
    return wyniki # Zwraca listę krotek np. [('01', 50.0), ('27', 450.0)]

def pobierz_sumy_kategorii(rok, miesiac):
    import sqlite3
    conn = sqlite3.connect('centus.db')
    c = conn.cursor()

    # Wyciągamy nazwę kategorii i sumę kwot dla danego miesiąca
    query = """
        SELECT kategoria, SUM(kwota) 
        FROM wydatki 
        WHERE strftime('%Y', data) = ? AND strftime('%m', data) = ?
        GROUP BY kategoria
        ORDER BY SUM(kwota) DESC
    """

    m_str = str(miesiac).zfill(2)
    c.execute(query, (str(rok), m_str))
    wyniki = c.fetchall()
    conn.close()
    # Zwraca np. [('Auto', 3613.0), ('Dom', 44.0)]
    return wyniki 


if __name__ == "__main__":
    inicjalizuj_baze()
    print("Baza danych jest gotowa do ataku.")