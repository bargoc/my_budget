import sqlite3
import logging


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
    limit_mie_sql = '''CREATE TABLE IF NOT EXISTS limit_wydatkow
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  rok INTEGER,
                  miesiac INTEGER,
                  limit_kwota REAL)'''

    # Tabela wydatków
    kursor.execute(wydatki_sql)
    
    # Tabela kategorii (na przyszłość)
    kursor.execute(kategorie_sql)

    kursor.execute(limit_mie_sql)
    
    conn.commit()
    conn.close()


def dodaj_poczatkowe_kategorie_db():
    poczatkowe = ['Żywność', 'Dom', 'Auto']
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
    # Ta funkcja przyjmuje 3 argumenty (kategorię, kwotę i użytkownika). 
    # Daty nie podajemy z zewnątrz, ponieważ funkcja sama ją sobie generuje w środku, 
    # w tej linijce: data_dzis = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
    # Dopiero później, wewnątrz funkcji, kiedy dochodzi do zapytania SQL: 
    # c.execute("INSERT INTO wydatki (data, kategoria, kwota, uzytkownik) VALUES (?, ?, ?, ?)", (data_dzis, kat, kwota, uzytkownik)) ...
    # używamy 4 wartości, aby wypełnić 4 znaki zapytania w tabeli.

def ukryj_kategorie_db():
    conn = sqlite3.connect('centus.db')
    c = conn.cursor()
    c.execute("UPDATE kategorie SET aktywna = 0 WHERE nazwa = ?", (nazwa,))
    # conn.commit()
    wyniki = c.fetchall()
    conn.close()
    return [k[0] for k in wyniki]

def przywroc_kategorie_db(nazwa):
    conn = sqlite3.connect('centus.db')
    c = conn.cursor()
    c.execute("UPDATE kategorie SET aktywna = 1 WHERE nazwa = ?", (nazwa,))
    conn.commit()
    conn.close()    

def pobierz_nieaktywne_kategorie_db():
    conn = sqlite3.connect('centus.db')
    kursor = conn.cursor()
    # Pobieramy tylko aktywne kategorie
    kursor.execute("SELECT nazwa FROM kategorie WHERE aktywna = 0 ORDER BY nazwa ASC")
    wyniki = kursor.fetchall()
    conn.close()
    return [k[0] for k in wyniki]    

def dodaj_wydatek_db(kat, kwota, uzytkownik="Basia"):
    from datetime import datetime
    data_dzis = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect('centus.db')
    c = conn.cursor()
    # INSERT OR IGNORE sprawi, że nie zdublujemy wpisów przy każdym starcie
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
    # SQLite potrzebuje miesiąca w formacie "04" a nie "4". Funkcja zfill() uzupełnia 0 z lewej strony
    m_str = str(miesiac).zfill(2)
    c.execute(query, (str(rok), m_str))
    # Metoda fetchall() pobiera wszystkie (lub wszystkie pozostałe) wiersze zestawu wyników zapytania i zwraca listę krotek .
    # Jeśli nie ma więcej dostępnych wierszy, zwraca pustą listę. 
    # Przed wykonaniem nowych instrukcji przy użyciu tego samego połączenia należy pobrać wszystkie wiersze dla bieżącego zapytania.
    wyniki = c.fetchall()
    conn.close()
    print(wyniki)
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
    # Nazwa pochodzi od "zero fill" (wypełnij zerami). Jej jedynym zadaniem jest upewnienie się, że ciąg znaków ma określoną długość.
    # Jeśli jest za krótki, funkcja dodaje zera zawsze z lewej strony.
    m_str = str(miesiac).zfill(2)
    c.execute(query, (str(rok), m_str))
    wyniki = c.fetchall()
    conn.close()
    # Zwraca np. [('Auto', 3613.0), ('Dom', 44.0)]
    return wyniki 

def ustaw_poczatkowy_limit():
    conn = sqlite3.connect('centus.db')
    c = conn.cursor()
    # Sprawdzamy czy tabela jest pusta
    c.execute("SELECT COUNT(*) FROM limit_wydatkow")
    if c.fetchone()[0] == 0:
        # Dodajemy domyślny limit na start
        c.execute("INSERT INTO limit_wydatkow (rok, miesiac, limit_kwota) VALUES (?, ?, ?)", 
                  (2026, 4, 3500.0))
        conn.commit()
    conn.close()

def pobierz_aktualny_limit():
    conn = sqlite3.connect('centus.db')
    c = conn.cursor()
    # Szukamy najnowszego limitu (wg daty)
    c.execute("SELECT limit_kwota FROM limit_wydatkow ORDER BY rok DESC, miesiac DESC LIMIT 1")
    
    wynik = c.fetchone()
    print(f"DEBUG: Pobrano z bazy: {wynik}") # TO CI POKAŻE CZY BAZA COŚ ZWRACA
    conn.close()
    
    if wynik is None:
        return 3500
    return wynik[0]  # Wartość awaryjna, jeśli tabela byłaby pusta 

    
    # return [0] if wynik else 3500.0  # Wartość awaryjna, jeśli tabela byłaby pusta

def zaktualizuj_limit(nowa_kwota):
    from datetime import datetime
    now = datetime.now()
    rok = now.year
    miesiac = now.month
    
    conn = sqlite3.connect('centus.db')
    c = conn.cursor()
    # Aktualizujemy limit
    c.execute("INSERT INTO limit_wydatkow (rok, miesiac, limit_kwota) VALUES (?, ?, ?)", (rok, miesiac, nowa_kwota))
   
    # Po insert niezbędny jest commit
    conn.commit()
    conn.close()

def pobierz_liste_wydatkow(rok, miesiac):
    conn = sqlite3.connect('centus.db')
    kursor = conn.cursor()
     # Pobieramy datę (sformatowaną), kategorię i kwotę
    query = "select data, kategoria, kwota from wydatki where strftime(%Y, data) = ? and strftime('%m', data) = ? order by data desc"
    kursor.execute(query, (str(rok), f"{miesiac:02d}"))
    dane = kursor.fetchall()
    conn.close()
    logging.debug('Pobieranie listy wszystkich miesięcznych wydatków')
    return dane

if __name__ == "__main__":
    inicjalizuj_baze()
    print("Baza danych jest gotowa do ataku.")