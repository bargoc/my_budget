import FreeSimpleGUI as sg
import wydatki_miesieczne as wm
import wydatki_wg_kategorii as kw
import db_manager as db
import sqlite3
from datetime import datetime
import widok_tabeli as wt
import moj_logger

# 1. Konfigurujemy logger JEDEN RAZ na samym początku uruchamiania aplikacji
moj_logger.skonfiguruj_logger()

# 2. Pobieramy instancję logera dla tego konkretnego pliku
logger = moj_logger.pobierz_logger('budzet')

# Przy starcie programu tworzymy tabele, jeśli nie istnieją
db.inicjalizuj_baze()

# 3. Zapisujemy komunikat
logger.debug('Inicjalizacja bazy danych')

# db.inicjalizuj_baze()

db.ustaw_poczatkowy_limit()
sg.theme('SystemDefaultForReal') # Lub np. 'LightBlue'
# Definiujemy listę kategorii (to co ma być w środku listy rozwijanej)
db.dodaj_poczatkowe_kategorie_db()
lista_kategorii = db.pobierz_kategorie_db()
# dotychczasowy_limit = db.pobierz_aktualny_limit()

layout = [
    [sg.Text("Budżet Domowy", font=("Arial", 18)), sg.Push(), sg.Button("⚙", key="Ustawienia", font=("Arial", 18), size=(2, 1))], 
    [sg.Text("Wybierz kategorię:")], 
    [sg.Combo(lista_kategorii, key='-KAT-', readonly=True, default_value=lista_kategorii[0], size=(21, 1))], 
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

def okno_urlop():
    kategorie_urlop = ["Podróż", "Noclegi", "Żywność", "Wejściówki", "Restauracja", "Bzdety"]
    naglowki = ["Data", "Kategoria", "Wydatki Basia", "Wydatki Ala", "Suma Skumulowana"]
    
    # Pobieramy dane startowe z bazy
    # dane_tabeli = pobierz_dane_urlopowe()
    dane_tabeli = db.pobierz_tabele_urlopowa()
    tekst_startowy_bilansu = generuj_tekst_bilansu() # Generujemy bilans na starcie

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
                  num_rows=15, alternating_row_color='lightgrey')],
        
        # --- NOWY ELEMENT: Pasek dynamicznego bilansu na jasnym, czytelnym tle ---
        [sg.Text(tekst_startowy_bilansu, key="-TEKST_BILANSU-", font=('Helvetica', 11, 'bold'), 
                 background_color='#E1F5FE', text_color='#0277BD', expand_x=True, justification='center', pad=(0,10))],

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
                kto = "Basia" if values["-R_BASIA-"] else "Alicja"
                dzis = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Zapis do bazy
                db.dodaj_wydatek_urlop(dzis, kat, kwota, kto)
                
                # 1. Odświeżenie tabeli
                nowe_dane = db.pobierz_tabele_urlopowa()
                win_urlop["-TABELA_URLOP-"].update(values=nowe_dane)
                
                # 2. ODŚWIEŻENIE BILANSU: Wyliczamy na nowo i aktualizujemy etykietę tekstową
                nowy_tekst = generuj_tekst_bilansu()
                win_urlop["-TEKST_BILANSU-"].update(value=nowy_tekst)
                
                win_urlop["-KWOTA-"].update("")
                
            except ValueError:
                sg.popup_error("Wprowadź poprawną kwotę!")

    win_urlop.close()

def generuj_tekst_bilansu():
    sumy = db.oblicz_bilans_wyjazdu()
    razem = sumy['Basia'] + sumy['Alicja']
    polowa = razem / 2
    
    # Kto wydał mniej, ten oddaje różnicę do połowy
    if sumy['Basia'] > sumy['Alicja']:
        do_zwrotu = polowa - sumy['Alicja']
        return f"Razem: {razem:.2f} zł  |  Alicja oddaje Basi: {do_zwrotu:.2f} zł"
    elif sumy['Alicja'] > sumy['Basia']:
        do_zwrotu = polowa - sumy['Basia']
        return f"Razem: {razem:.2f} zł  |  Basia oddaje Alicji: {do_zwrotu:.2f} zł"
    else:
        return f"Razem: {razem:.2f} zł  |  Wydatki idealnie równe!"


def odswiez_liste_kategorii(window):
    nowe_kategorie = db.pobierz_kategorie_db() # Twoja funkcja pobierająca listę
    
    # Zabezpieczenie: Sprawdzamy czy window nie jest None i czy posiada element o tym kluczu
    if window and not window.was_closed():
        # Używamy klucza, który faktycznie znajduje się w layoucie głównego okna
        # Sprawdź w layoucie: czy to na pewno '-KAT-' czy '-COMBO_KAT-'?
        try:
            window['-KAT-'].update(values=nowe_kategorie)
        except KeyError:
            print("Błąd: Nie znaleziono klucza '-KAT-' w głównym oknie.")
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

while True:
    event, values = window.read()
    print(f"event: {event}")
    if event in (sg.WIN_CLOSED, "Wyjście"):
        break 

    if event == "Dodaj zakup":
        kat = values['-KAT-']
        # Zamiana przecinka na kropkę
        kwota_str = values['-KWOTA-'].replace(',', '.')
        try:
            kwota = float(kwota_str)
            db.dodaj_wydatek_db(kat, kwota, uzytkownik="Basia")
            
            # Resetowanie pola kwoty i potwierdzenie zmiany
            window['-KWOTA-'].update('')
            logger.debug('Dodanie wydatku')
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
                    # 1. Wywołujemy czystą logikę z bazy danych
                    typ_msg, tresc_msg = db.zarzadzaj_dodawaniem_kategorii(n_kat)

                    # 2. Wyświetlamy odpowiedni komunikat w GUI
                    if typ_msg == "quick":
                        sg.popup_quick_message(tresc_msg)
                    elif typ_msg == "error":
                        sg.popup_error("Ta kategoria już istnieje i jest aktywa.")

                    # 3. Odświeżamy listę w oknach korzystając z gotowej metody

                    # Odświeżamy widoki w obu oknach
                    nowa_lista = db.pobierz_kategorie_db()
                    # Aktualizacja listy w oknie ustawień
                    # Czyszczenie pola wejściowego po dodaniu (zakładam, że pole Input ma klucz '-NEW-') Czyścimy Input 
                    win_sett['-LISTA-'].update(nowa_lista)

                    # Aktualizacja Combo w oknie głównym (jeśli obiekt głównego okna istnieje)
                    if window:
                        window['-KAT-'].update(values=nowa_lista) # użyj właściwego klucza Twojego Combo
                   
            
            if e_set == "Ukryj kategorię":
                wybrana_z_listy = v_set['-LISTA-']
                logger.debug('Próba pokazania kategorii') # To zwraca np. ['Odzież']
                if wybrana_z_listy:  # Sprawdzamy, czy użytkownik w ogóle coś kliknął
                    wybrana = wybrana_z_listy[0] # <--- TUTAJ wyciągamy czysty tekst: 'Odzież'
                    
                    # Teraz przekazujemy czysty tekst do bazy danych
                    nowa_lista = db.ukryj_kategorie_db(wybrana)
                    logger.debug('Kategorie ukryta - pudło')
                    # Odświeżamy widok w GUI
                    win_sett['-LISTA-'].update(nowa_lista)
                    sg.popup_quick_message(f"Ukryto kategorię: {wybrana[0]}")

                    logger.debug('Kategorie ukryta - pudło')
                    if window:
                        logger.debug('1')
                        window['-KAT-'].update(values=nowa_lista)
                        logger.debug('2')
                    # Czyścimy Input                    
                    win_sett['-LISTA-'].update(nowa_lista)
            
            if e_set == "Odzyskaj kategorię":
                wybrana_z_listy = v_set['-LISTAUKRYTYCH-']
                # ZABEZPIECZENIE: Sprawdzamy, czy użytkownik zaznaczył coś na liście
                if wybrana_z_listy and len(wybrana_z_listy) > 0:
                    wybrana = wybrana_z_listy[0]  # Wyciągamy czysty tekst z listy PySimpleGUI
                    # 2. Pobranie ŚWIEŻYCH danych dla obu list
                    # 1. Przenosimy logikę do managera bazy
                    db.przywroc_kategorie_db(wybrana)
                    # 1. CZISTA LOGIKA: Wywołujemy funkcję z managera i odbieramy gotowe listy
                    nowe_aktywne = db.pobierz_kategorie_db()
                    nowe_nieaktywne = db.pobierz_nieaktywne_kategorie_db()
                   
                   # 3. Aktualizacja GUI (Wszystkich miejsc!)
                    win_sett['-LISTA-'].update(values=nowe_aktywne)
                    win_sett['-LISTAUKRYTYCH-'].update(values=nowe_nieaktywne)
                    if window:
                        window['-KAT-'].update(values=nowe_aktywne)
                    sg.popup_quick_message(f"Przywrócono kategorię: {wybrana}")

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







