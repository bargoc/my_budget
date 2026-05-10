import FreeSimpleGUI as sg
import wydatki_miesieczne as wm
import wydatki_wg_kategorii as kw
import db_manager as db
import sqlite3
import logging

logging.basicConfig(filename='DebugInfo.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
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
    [sg.Button("Wyjście", size=(22, 1)), sg.Button("Ustawienia", size=(4, 1))], # NOWY PRZYCISKsg.Button("Wyjście", size=(22, 1))]
    # [sg.Button("Wyjście", size=(22, 1))]
]

window = sg.Window("Centuś", layout)

# Tymczasowa lista na dsiejsze zakupy
# dzisiejsze_wpisy = []

def odswiez_liste_kategorii(window):
    nowe_kategorie = db.pobierz_kategorie() # Twoja funkcja pobierająca listę
    
    # ZABEZPIECZENIE:
    if window and not window.was_closed():
        window['-COMBO-'].update(values=nowe_kategorie)
    else:
        print("Nie mogę odświeżyć listy – okno jest zamknięte.")

""" def odswiez_aktywne_kategorie(window):
    nowe_kategorie = db.pobierz_kategorie() # Twoja funkcja pobierająca listę
    
    # ZABEZPIECZENIE:
   # Aktualizujesz konkretne okno, które dostałaś jako argument
    if window:
        window['-LISTA-'].update(values=nowa_lista)
        # Opcjonalnie: jeśli chcesz też odświeżyć główne okno:
        # window_glowne['-KAT-'].update(values=nowa_lista) """

while True:
    event, values = window.read()
    print(f"event 1 {event}")
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
            sg.popup_quick_message(f"Zapisano w bazie: {kwota} zł ({kat})", background_color="green", text_color="white")

        except ValueError:
            sg.popup_error("Wpisz poprawną liczbę")

    if event == "Pokaż wykres skumulowany":
        # Wywołujesz funkcję, którą przed chwilą dopracowałaś
        wm.wydatki_dzienne_skumulowane()

    if event == "Pokaż kategorie":
        kw.wydatki_kategorie()
    """ 
    if event == " + ":
        nowa = values['-NOWA_KAT-'].strip()
        if nowa:
            conn = sqlite3.connect('centus.db')
            kursor = conn.cursor()
            try:
                # 1. NAJPIERW DODAJEMY DO BAZY (tego brakowało!)
                # {nowa} vs (nowa,): W SQL (sqlite3) argumenty podajemy zawsze jako krotkę (tuple) w nawiasach okrągłych z przecinkiem, 
                # a nie w klamrach {}.
                kursor.execute("INSERT INTO kategorie (nazwa, aktywna) VALUES (?, 1)", (nowa,))
                conn.commit()
                
                # 2. POTEM ODŚWIEŻAMY COMBO (pobieramy nową listę z bazy)
                nowa_lista = db.pobierz_kategorie_db()
                window['-KAT-'].update(values=nowa_lista, value=nowa)
                
                # 3. CZYŚCIMY POLE WPISYWANIA
                window['-NOWA_KAT-'].update('')
                sg.popup_quick_message(f"Dodano kategorię: {nowa}", background_color="green")
                
            except sqlite3.IntegrityError:
                sg.popup_error("Taka kategoria już istnieje!")
            finally:
                conn.close() """

    # window.close()

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
            
            if event == "Pokaż wykres skumulowany":
                wm.wydatki_dzienne_skumulowane()

            if event == "Pokaż kategorie":
                kw.wydatki_kategorie()

        window.close()

# print([m for m in dir(sg.Combo) if not m.startswith('_')])







