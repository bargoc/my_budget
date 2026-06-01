import sqlite3
import moj_logger  # Import naszego modułu

# Pobieramy logger i nazywamy go nazwą tego modułu
logger = moj_logger.pobierz_logger('BazaDanych')

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
    urlop_sql = '''CREATE TABLE IF NOT EXISTS wydatki_urlop (id INTEGER PRIMARY KEY AUTOINCREMENT, data TEXT, kategoria TEXT, kwota REAL, uzytkownik TEXT)'''

    # Tabela wydatków
    kursor.execute(wydatki_sql)
    
    # Tabela kategorii (na przyszłość)
    kursor.execute(kategorie_sql)

    kursor.execute(limit_mie_sql)

    kursor.execute(urlop_sql)
    
    conn.commit()
    conn.close()

# **************************  URLOP  **************************
def pobierz_tabele_urlopowa():
    """Pobiera dane z bazy i przygotowuje je bezpośrednio w formacie dla widgetu sg.Table."""
    conn = sqlite3.connect('centus.db')
    cursor = conn.cursor()
    
    # Pobieramy wydatki posortowane chronologicznie
    cursor.execute("SELECT data, kategoria, kwota, uzytkownik FROM wydatki_urlop ORDER BY data ASC")
    wiersze = cursor.fetchall()
    conn.close()

    tabela_gui = []
    suma_skumulowana = 0.0

    for data, kategoria, kwota, uzytkownik in wiersze:
        suma_skumulowana += kwota
        
        # Rozdzielamy kwoty na odpowiednie kolumny
        kwota_basia = f"{kwota:.2f}" if uzytkownik == 'Basia' else ""
        kwota_ala = f"{kwota:.2f}" if uzytkownik == 'Ala' else ""
        
        # Tworzymy wiersz (skracamy datę do formatu RRRR-MM-DD)
        tabela_gui.append([
            data[:10], 
            kategoria,
            kwota_basia,
            kwota_ala,
            f"{suma_skumulowana:.2f}"
        ])
        
    return tabela_gui


def dodaj_wydatek_urlop(data, kategoria, kwota, uzytkownik):
    """ Wstawia do tabeli urlopowej i do bazy wydatek jednego z dwóch urlopowiczów. """
    conn = sqlite3.connect('centus.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO wydatki_urlop (data, kategoria, kwota, uzytkownik) VALUES (?, ?, ?, ?)
    ''', (data, kategoria, float(kwota), uzytkownik))
    conn.commit()
    conn.close()

# Ta funkcja jest przykładem, jak można pobrać dane z bazy i przygotować je w formacie odpowiednim dla widgetu sg.Table.
def oblicz_bilans_wyjazdu():
    """Pobiera sumę wydatków Basi i Ali dla CAŁEGO wyjazdu."""
    conn = sqlite3.connect('centus.db') # używamy Twojej testowej nazwy bazy
    cursor = conn.cursor()
    
    query = """
        SELECT uzytkownik, SUM(kwota) 
        FROM wydatki_urlop 
        GROUP BY uzytkownik
    """
    cursor.execute(query)
    dane = cursor.fetchall()
    conn.close()

    sumy = {'Basia': 0.0, 'Alicja': 0.0}
    for uzytkownik, kwota in dane:
        if uzytkownik in sumy:
            sumy[uzytkownik] = kwota if kwota else 0.0
            
    return sumy

# **************************  KATEGORIE  **************************
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
    """Pobiera wyłącznie AKTYWNE kategorie."""
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

def ukryj_kategorie_db(nazwa_kategorii):
    # Ukrywa kategorię w bazie i zwraca nową listę aktywnych kategorii.
    conn = sqlite3.connect('centus.db')
    c = conn.cursor()
    # 1. Wykonujemy zmianę (używamy zmiennej przekazanej w argumencie)
    c.execute("UPDATE kategorie SET aktywna = 0 WHERE nazwa = ?", (nazwa_kategorii,))
    # 2. KONIECZNIE zatwierdzamy zmiany w pliku bazy danych
    conn.commit()
    # 2. JAWNIE pytamy bazę o nową, zaktualizowaną listę aktywnych kategorii
    c.execute("SELECT nazwa FROM kategorie WHERE aktywna = 1 ORDER BY nazwa ASC")
    # 3. Od razu pobieramy świeżą listę aktywnych kategorii, żeby przekazać ją do GUI
    wyniki = c.fetchall()
    conn.close()
    # Zwracamy czystą listę tekstową, np. ['Auto', 'Dom', 'Żywność']
    return [k[0] for k in wyniki]

def przywroc_kategorie_db(nazwa_kategorii):
    """Modyfikuje status kategorii na aktywny."""
    conn = sqlite3.connect('centus.db')
    c = conn.cursor()
    
    # 1. Przywracamy kategorię
    c.execute("UPDATE kategorie SET aktywna = 1 WHERE nazwa = ?", (nazwa_kategorii,))
    conn.commit()
    conn.close()

def pobierz_nieaktywne_kategorie_db():
    """Pobiera wyłącznie UKRYTE (nieaktywne) kategorie."""
    conn = sqlite3.connect('centus.db')
    kursor = conn.cursor()
    # Pobieramy tylko aktywne kategorie
    kursor.execute("SELECT nazwa FROM kategorie WHERE aktywna = 0 ORDER BY nazwa ASC")
    wyniki = kursor.fetchall()
    conn.close()
    return [k[0] for k in wyniki]    


    

def pobierz_wydatki_miesieczne(rok, miesiac):
    logger.debug(f'Próba dodania wydatku: {rok, miesiac}')
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

def dodaj_wydatek_db(kat, kwota, uzytkownik="Basia"):
    from datetime import datetime
    data_dzis = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect('centus.db')
    c = conn.cursor()
    # INSERT OR IGNORE sprawi, że nie zdublujemy wpisów przy każdym starcie
    c.execute("INSERT INTO wydatki (data, kategoria, kwota, uzytkownik) VALUES (?, ?, ?, ?)",
              (data_dzis, kat, kwota, uzytkownik))
    conn.commit()
    logger.info(f'Pomyślnie zaktualizowano bazę dla wydatku: {kwota}')
    conn.close()

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
    cursor = conn.cursor()
    # Pobieramy datę (sformatowaną), kategorię i kwotę
    query = """
        SELECT ID, data, kategoria, kwota 
        FROM wydatki 
        WHERE strftime('%Y', data) = ? AND strftime('%m', data) = ?
        ORDER BY data DESC
    """
    cursor.execute(query, (str(rok), f"{miesiac:02d}"))
    dane = cursor.fetchall()
    conn.close()
    return dane

def usun_wydatek(id_wydatku):
    conn = sqlite3.connect('centus.db')
    cursor = conn.cursor()
    cursor.execute("delete from wydatki where id = ?", (id_wydatku,))
    conn.commit()
    conn.close()

def pobierz_sumy_dzienne(rok, miesiac):
    conn = sqlite3.connect('centus.db')
    cursor = conn.cursor()
    # Pobieramy dzień miesiąca i sumę wydatków z tego dnia
    query = """
        SELECT strftime('%d', data) as dzien, SUM(kwota) 
        FROM wydatki 
        WHERE strftime('%Y', data) = ? AND strftime('%m', data) = ?
        GROUP BY dzien
        ORDER BY dzien ASC
    """
    cursor.execute(query, (str(rok), f"{miesiac:02d}"))
    dane = cursor.fetchall()
    conn.close()
    return dane # Zwraca listę krotek np. [('01', 50.0), ('05', 120.0)]

def pobierz_limit(rok, miesiac):
    conn = sqlite3.connect('centus.db')
    cursor = conn.cursor()
    
    # Usuwamy 'group by', bo filtrujemy konkretny okres
    query = """ 
        SELECT limit_kwota 
        FROM limit_wydatkow  
        WHERE strftime('%Y', limit_kwota) = ? AND strftime('%m', limit_kwota) = ?
    """    
    
    cursor.execute(query, (str(rok), f"{miesiac:02d}"))
    wynik = cursor.fetchone() # Pobieramy tylko jeden (pierwszy) pasujący rekord
    conn.close()
    
    # Logika bezpieczeństwa:
    # Jeśli wynik istnieje, bierzemy pierwszą wartość z krotki wynik[0]
    # W przeciwnym razie zwracamy 0.0, żeby wykres się nie "rozsypał"
    return wynik[0] if wynik else 0.0

# Pobieramy numer miesiąca i sumę wydatków dla tego miesiąca
def pobierz_sumy_miesieczne_w_roku(rok):
    conn = sqlite3.connect('centus.db')
    cursor = conn.cursor()
    
    # Pobieramy numer miesiąca i sumę wydatków dla tego miesiąca
    query = """
        SELECT strftime('%m', data) as miesiac, SUM(kwota) 
        FROM wydatki 
        WHERE strftime('%Y', data) = ?
        GROUP BY miesiac
        ORDER BY miesiac ASC
    """
    cursor.execute(query, (str(rok),))
    dane = cursor.fetchall()
    conn.close()
    return dane # Zwraca listę krotek, np. [('01', 1200.50), ('02', 950.00)]



def zarzadzaj_dodawaniem_kategorii(n_kat):
    # Logika SQL dla dodawania kategorii.
    # Zwraca krotkę: (typ_komunikatu, tresc_komunikatu)
    conn = sqlite3.connect('centus.db')
    kursor = conn.cursor()

    # 1. Sprawdzamy, czy taka kategoria już istnieje
    kursor.execute("SELECT aktywna FROM kategorie WHERE nazwa = ?", (n_kat,))
    istnieje = kursor.fetchone()

    # status = ()
    if istnieje is not None:

        if istnieje[0] == 0:
            # Jeśli jest ukryta, to ją aktywujemy
            kursor.execute("UPDATE kategorie SET aktywna = 1 WHERE nazwa = ?", (n_kat,))
            status = ("quick", f"Przywrócono kategorię: {n_kat}")
        else:
            # 2. Jeśli nie istnieje, dodajemy nową            
            status = ("error", f"Dodano nową kategorię: {n_kat}")
    else:
        kursor.execute("INSERT INTO kategorie (nazwa, aktywna) VALUES (?, 1)", (n_kat,))
        status = ("quick", f"Dodano nową kategorię: {n_kat}")

    conn.commit()
    conn.close()
    return status

if __name__ == "__main__":
    inicjalizuj_baze()
    print("Baza danych jest gotowa do ataku.")
