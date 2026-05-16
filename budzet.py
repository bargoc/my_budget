import FreeSimpleGUI as sg
import wydatki_miesieczne as wm
import wydatki_wg_kategorii as kw
import db_manager as db
import sqlite3
import logging
from datetime import datetime
import widok_tabeli as wt

logging.basicConfig(filename='DebugInfo.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('matplotlib').setLevel(logging.WARNING)
# Przy starcie programu tworzymy tabele, jeśli nie istnieją
db.inicjalizuj_baze()
logging.debug('Inicjalizacja bazy danych')
db.ustaw_poczatkowy_limit()
logging.debug('Start programu')
sg.theme('SystemDefaultForReal') # Lub np. 'LightBlue'
# Definiujemy listę kategorii (to co ma być w środku listy rozwijanej)
db.dodaj_poczatkowe_kategorie_db()
lista_kategorii = db.pobierz_kategorie_db()
# dotychczasowy_limit = db.pobierz_aktualny_limit()

layout = [
    [sg.Text("Budżet Domowy", font=("Arial", 18)), sg.Push(), sg.Button("⚙", key="Ustawienia", font=("Arial", 18), size=(2, 1))], 
    [sg.Text("Wybierz kategorię:")], 
    [sg.Combo(lista_kategorii, key='-KAT-', readonly=True, default_value=lista_kategorii[0], size=(21, 1))], 
    # [sg.Text("Dodaj nową kategorię:")],
    # [sg.Input(key='-NOWA_KAT-', size=(23, 1)), sg.Button(" + ")],
    [sg.Text("Kwota:")],
    [sg.Input(key='-KWOTA-', size=(23, 1))],
    
    # Akceptacja pojedynczego zakupu
    # bind_return_key=True: To "ficzer", który pozwala na zatwierdzenie zakupu po prostu naciskając Enter na klawiaturze,
    # bez odrywania rąk od pisania kwot.
    [sg.Button("Dodaj zakup", bind_return_key=True, button_color=('white', 'green'), size=(22, 1))],
    
    [sg.HorizontalSeparator(), sg.Text('         ')], # Estetyczna linia oddzielająca
    [sg.Button("Pokaż wykres skumulowany", size=(22, 1))],

    [sg.Button("Pokaż kategorie", size=(22, 1))],
    [sg.Button("Lista wydatków", size=(22, 1))],
    [sg.Button("Urlop Duo", size=(22, 1))],
    [sg.Button("Wykres roczny", size=(12, 1)), sg.Button("Wyjście", size=(8, 1))], # NOWY PRZYCISKsg.Button("Wyjście", size=(22, 1))]
    # [sg.Button("Wyjście", size=(22, 1))]
]

window = sg.Window("Centuś", layout)

def pobierz_dane_urlopowe():
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
        
        # Rozdzielamy kwoty na kolumny w zależności od tego, kto płacił
        kwota_basia = f"{kwota:.2f}" if uzytkownik == 'Basia' else ""
        kwota_ala = f"{kwota:.2f}" if uzytkownik == 'Ala' else ""
        
        # Tworzymy wiersz do wyświetlenia w GUI
        tabela_gui.append([
            data[:10], # Tylko data RRRR-MM-DD bez godzin
            kategoria,
            kwota_basia,
            kwota_ala,
            f"{suma_skumulowana:.2f}" # Suma narastająca dzień po dniu
        ])
        
    return tabela_gui

def okno_urlop():
    kategorie_urlop = ["Podróż", "Noclegi", "Żywność", "Wejściówki", "Restauracja"]
    naglowki = ["Data", "Kategoria", "Wydatki Basia", "Wydatki Ala", "Suma Skumulowana"]
    
    # Pobieramy dane startowe z bazy
    dane_tabeli = pobierz_dane_urlopowe()

    layout = [
        [sg.Text("🌴 Moduł Urlopowy – Bilans Wspólny", font=('Helvetica', 14, 'bold'))],
        
        # Sekcja wprowadzania nowego wydatku
        [sg.Frame("Dodaj wydatek urlopowy", [
            [sg.Text("Kategoria:"), sg.Combo(kategorie_urlop, default_value="Żywność", key="-KAT-", readonly=True),
             sg.Text("Kwota:"), sg.Input(size=(10,1), key="-KWOTA-")],
            [sg.Text("Kto płacił:"), 
             sg.Radio("Basia", "KTO", key="-R_BASIA-", default=True), 
             sg.Radio("Alicja", "KTO", key="-R_ALA-"),
             sg.Push(), sg.Button("Dodaj wpis", key="-DODAJ_URLOP-")]
        ])],
        
        # Główna lista wydatków do kontroli zapisów
        [sg.Table(values=dane_tabeli, headings=naglowki, auto_size_columns=True,
                  display_row_numbers=False, justification='center', key="-TABELA_URLOP-",
                  num_rows=15, alternating_row_color='red')],
        
        [sg.Button("Zamknij")]
    ]

    win_urlop = sg.Window("Urlop z Alicją", layout, modal=True, finalize=True)

    while True:
        event, values = win_urlop.read()
        if event in (sg.WIN_CLOSED, "Zamknij"):
            break
            
        if event == "-DODAJ_URLOP-":
            # Logika dodawania
            try:
                kwota = float(values["-KWOTA-"].replace(',', '.'))
                kat = values["-KAT-"]
                kto = "Basia" if values["-R_BASIA-"] else "Ala"
                dzis = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Zapis do bazy
                db.dodaj_wydatek_urlop(dzis, kat, kwota, kto)
                
                # Odświeżenie tabeli w oknie
                nowe_dane = pobierz_dane_urlopowe()
                win_urlop["-TABELA_URLOP-"].update(values=nowe_dane)
                win_urlop["-KWOTA-"].update("") # czyszczenie pola kwoty
                
            except ValueError:
                sg.popup_error("Wprowadź poprawną kwotę!")

    win_urlop.close()

    
def odswiez_liste_kategorii(window):
    nowe_kategorie = db.pobierz_kategorie() # Twoja funkcja pobierająca listę
    
    # ZABEZPIECZENIE:
    if window and not window.was_closed():
        window['-COMBO-'].update(values=nowe_kategorie)
    else:
        print("Nie mogę odświeżyć listy – okno jest zamknięte.")

def okno_wyboru_daty():
    dzis = datetime.now()
    lata = [dzis.year, dzis.year - 1, dzis.year - 2]
    miesiace = [f"{i:02d}" for i in range(1, 13)]

    layout = [
        [sg.Text("Wybierz okres dla wykresu:")],
        [sg.Text("Miesiąc:"), sg.Combo(miesiace, default_value=dzis.strftime("%m"), key='-MIESIAC-', readonly=True, size=(10,1))],
        [sg.Text("Rok:", size=(6,1)), sg.Combo(lata, default_value=dzis.year, key='-ROK-', readonly=True, size=(10,1))],
        [sg.Button("OK", size=(8,1)), sg.Button("Anuluj", size=(8,1))]
    ]

    window = sg.Window("Wybierz datę", layout, modal=True)
    wybrana_data = None

    while True:
        event, values = window.read()
        if event == "OK":
            wybrana_data = (int(values['-ROK-']), int(values['-MIESIAC-']))
            break
        if event in (sg.WIN_CLOSED, "Anuluj"):
            break
    
    window.close()
    return wybrana_data

def okno_wyboru_roku():
    dzis = datetime.now()
    # ???
    lata = [dzis.year, dzis.year - 1, dzis.year - 2]
    layout =[
        [sg.Text("Wybierz rocznik wykresu: ")],
        [sg.Text("Rok:"), sg.Combo(lata, default_value=dzis.year, key='-ROK-', readonly=True)],
        [sg.Button("OK"), sg.Button("Anuluj")]
    ]
    window = sg.Window("Wybierz rok", layout, modal=True)
    wybrany_rok = None

    while True:
        event, values = window.read()
        if event == "OK":
            wybrany_rok = int(values['-ROK-'])
            break
        if event in (sg.WIN_CLOSED, "Anuluj"):
            break
    window.close()
    return wybrany_rok

""" def okno_ustawien():
    win_sett = sg.Window("Ustawienia", layout)
    while True:
        e_set, v_set = win_sett.read()
        if e_set in (sg.WIN_CLOSED, "Zamknij"):
            # 1. Kliknięcie powoduje WYJŚCIE z pętli...
            break  

    # <--- TUTAJ JESTEŚMY PO KLIKNIĘCIU "ZAMKNIJ"
    # Jeśli w tym miejscu brakuje poniższej linijki:
    win_sett.close() """

while True:
    event, values = window.read()
    print(f"event: {event}")
    logging.debug(f"Zdarzenie: {event}")
    if event in (sg.WIN_CLOSED, "Wyjście"):
        break 

    if event == "Dodaj zakup":
        kat = values['-KAT-']
        # Zamiana przecinka na kropkę
        kwota_str = values['-KWOTA-'].replace(',', '.')
        try:
            kwota = float(kwota_str)
            db.dodaj_wydatek_db(kat, kwota, uzytkownik="Basia")
            logging.debug('Dodanie wydatku')
            # Resetowanie pola kwoty i potwierdzenie zmiany
            window['-KWOTA-'].update('')
            logging.debug('Dodanie wydatku')
            sg.popup_quick_message(f"Zapisano w bazie: {kwota} zł ({kat})", background_color="green", text_color="white")

        except ValueError:
            sg.popup_error("Wpisz poprawną liczbę")
    
    if event == "Pokaż kategorie":
        data = okno_wyboru_daty()
        if data:
            rok, miesiac = data
            kw.wydatki_kategorie(rok, miesiac)
    
    if event == "Pokaż wykres skumulowany":
        data = okno_wyboru_daty()
        if data:
            rok, miesiac = data
            # wm.wykres_skumulowany(rok, miesiac)
            wm.wydatki_dzienne_skumulowane()

    if event == "Wykres roczny":
        rok = okno_wyboru_roku()
        if rok:
            wm.wykres_roczny(rok)

    if  event == "Urlop Duo":
        """ data = okno_urlop
        if data:
            uzytkownik = data """
            # Po prostu wywołujemy okno. Ono zajmie się resztą.
        okno_urlop()
# "Data", "Kategoria", "Wydatki Basia", "Wydatki Ala", "Suma Skumulowana"           
 
    if event == "Ustawienia":
        # Tworzymy układ nowego okna
        # dotychczasowy_limit = db.pobierz_aktualny_limit()
        layout_settings = [
            [sg.Text("Zarządzanie kategoriami")],
            [sg.Input(key='-NEW-', size=(20, 1)), sg.Button("Dodaj")],
            [sg.Listbox(values=db.pobierz_kategorie_db(), size=(20, 5), key='-LISTA-')],
            [sg.Button("Ukryj kategorię", size=(19, 1))], 
            [sg.Button("Odzyskaj kategorię", size=(19, 1)), sg.Listbox(key='-LISTAUKRYTYCH-', values=db.pobierz_nieaktywne_kategorie_db(), size=(10, 1))], 
            # [sg.Button("Usuń z bazy", size=(19, 1))], 
            # [sg.Text(f"Zmiana limitu {dotychczasowy_limit}", keys='-LIMIT_TEXT_')],
            [sg.Text(f"Zmiana limitu")],
            [sg.Input(key='-CURRENTLIMIT-', size=(20,1)), sg.Button("Zmień")],
            [sg.Text(key='-INFO_LIMIT-')],
            [sg.Button("Zamknij", size=(19, 1))]   
        ]
        # modal=True: To ważny argument w sg.Window. Sprawia on, że dopóki nie zamkniesz Ustawień, nie możesz klikać w głównym oknie Centusia.
        # To zapobiega błędom i "bałaganowi" w bazie danych.

        win_sett = sg.Window("Ustawienia", layout_settings, modal=True)

        while True:
            e_set, v_set = win_sett.read()
            if e_set in (sg.WIN_CLOSED, "Zamknij"):
                print("LOG: Przechwycono zdarzenie zamknięcia! Wychodzę z pętli.")
                break

                
            if e_set == "Dodaj":
                n_kat = v_set['-NEW-'].strip()
                if n_kat:
                    conn = sqlite3.connect('centus.db') 
                    c = conn.cursor()

                    # 1. Sprawdzamy, czy taka kategoria już w ogóle istnieje (nawet ukryta)
                    # Jeśli jest ukryta, to ją aktywujemy
                    c.execute("SELECT aktywna FROM kategorie WHERE nazwa = ?", (n_kat,))
                    istnieje = c.fetchone()
                    
                    if istnieje:
                        if istnieje[0] == 0:
                            # Jeśli jest ukryta, to ją aktywujemy
                            c.execute("UPDATE kategorie SET aktywna = 1 WHERE nazwa = ?", (n_kat,))
                            # odswiez_liste_kategorii()
                            sg.popup_quick_message(f"Przywrócono kategorię: {n_kat}")
                        else:
                            sg.popup_error("Ta kategoria jest już aktywna!")
                    else:
                        # 2. Jeśli nie istnieje, dodajemy nową
                        c.execute("INSERT INTO kategorie (nazwa, aktywna) VALUES (?, 1)", (n_kat,))
                        sg.popup_quick_message(f"Dodano nową kategorię: {n_kat}")

                    conn.commit()
                    conn.close()

                    # Odświeżamy widoki w obu oknach
                    nowa_lista = db.pobierz_kategorie_db()
                    # Aktualizacja listy w oknie ustawień
                    # win_sett['-LISTA-'].update(nowa_lista)

                    # Aktualizacja Combo w głównym oknie
                    if window:
                        win_sett['-LISTA-'].update(nowa_lista)
                    # Czyścimy Input                    
                    win_sett['-LISTA-'].update(nowa_lista)
                   
            
            if e_set == "Ukryj kategorię":
                wybrana = v_set['-LISTA-']
                if wybrana:
                    conn = sqlite3.connect('centus.db')
                    c = conn.cursor()
                    c.execute("UPDATE kategorie SET aktywna = 0 WHERE nazwa = ?", (wybrana[0],))

                    conn.commit()
                    conn.close()
                    nowa_lista = db.pobierz_kategorie_db()
                    # win_sett['-LISTA-'].update(nowa_lista)
                    # window['-KAT-'].update(values=nowa_lista) 

                    if window:
                        window['-KAT-'].update(values=nowa_lista)
                    # Czyścimy Input                    
                    win_sett['-LISTA-'].update(nowa_lista)
            
            if e_set == "Odzyskaj kategorię":
                wybrana = v_set['-LISTAUKRYTYCH-']
                if wybrana:
                    conn = sqlite3.connect('centus.db')
                    c = conn.cursor()
                    c.execute("UPDATE kategorie SET aktywna = 1 WHERE nazwa = ?", (wybrana[0],))
                    # odswiez_liste_kategorii()
                    conn.commit()
                    conn.close()
                    # 2. Pobranie ŚWIEŻYCH danych dla obu list
                    nowe_aktywne = db.pobierz_kategorie_db()
                    nowe_nieaktywne = db.pobierz_nieaktywne_kategorie_db()
                    # win_sett['-LISTA-'].update(nowa_lista)
                    # window['-KAT-'].update(values=nowa_lista)
                   # 3. Aktualizacja GUI (Wszystkich miejsc!)
                    win_sett['-LISTA-'].update(values=nowe_aktywne)
                    win_sett['-LISTAUKRYTYCH-'].update(values=nowe_nieaktywne)
                    if window:
                        window['-KAT-'].update(values=nowe_aktywne)
        
            # Zmiana limitu 
            if e_set == 'Zmień':
                nowy_limit_str = v_set['-CURRENTLIMIT-'].replace(',', '.')
                try:
                    nowa_kwota = float(nowy_limit_str)
                    # Tutaj wywołujesz funkcję, która doda nowy wiersz do tabeli
                    # z datą '2026-05-01' (albo bieżącą datą)
                    db.zaktualizuj_limit(nowa_kwota) 
                    
                    sg.popup_quick_message("Limit zaktualizowany!")
                    # Odświeżamy napis w GUI
                    win_sett['-CURRENTLIMIT-'].update('')
                    # 2. Opcjonalnie: Jeśli masz tekst informujący o aktualnym limicie, zaktualizuj go:
                    win_sett['-INFO_LIMIT-'].update(f"Aktualny limit wynosi: {nowa_kwota} zł")
                except ValueError:
                    sg.popup_error("Wpisz poprawną liczbę!")   

        window.close()
                 

    if event == "Lista wydatków":
        wt.okno_listy_wydatkow()

print(f"Ostatnia linia widnows.close(). Zdarzenie: {event}") 
window.close()

# print([m for m in dir(sg.Combo) if not m.startswith('_')])







