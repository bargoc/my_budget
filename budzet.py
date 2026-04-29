import FreeSimpleGUI as sg
import wydatki_miesieczne as wm
import wydatki_wg_kategorii as kw
import db_manager as db
import sqlite3

# Przy starcie programu tworzymy tabele, jeśli nie istnieją
db.inicjalizuj_baze()

sg.theme('SystemDefaultForReal') # Lub np. 'LightBlue'
# Definiujemy listę kategorii (to co ma być w środku listy rozwijanej)
db.dodaj_poczatkowe_kategorie_db()
lista_kategorii = db.pobierz_kategorie_db()


layout = [
    [sg.Text("Budżet Domowy", font=("Arial", 18)), sg.Push(), sg.Button("⚙", key="Ustawienia", font=("Arial", 18), size=(2, 1))], 
    [sg.Text("Wybierz kategorię:")], 
    [sg.Combo(lista_kategorii, key='-KAT-', readonly=True, default_value=lista_kategorii[0], size=(21, 1))], 
    # [sg.Text("Dodaj nową kategorię:")],
    # [sg.Input(key='-NOWA_KAT-', size=(23, 1)), sg.Button(" + ")],
    [sg.Text("Kwota:")],
    [sg.Input(key='-KWOTA-', size=(23, 1))],
    
    # NOWY PRZYCISK: Akceptacja pojedynczego zakupu
    [sg.Button("Dodaj zakup", bind_return_key=True, button_color=('white', 'green'), size=(22, 1))],
    
    [sg.HorizontalSeparator(), sg.Text('         ')], # Estetyczna linia oddzielająca
    [sg.Button("Pokaż wykres skumulowany", size=(22, 1))],
    [sg.Button("Pokaż kategorie", size=(22, 1))],
    # [sg.Button("Wyjście", size=(22, 1)), sg.Button("Ustawienia", size=(4, 1))], # NOWY PRZYCISKsg.Button("Wyjście", size=(22, 1))]
    [sg.Button("Wyjście", size=(22, 1)), sg.Push()]
]

window = sg.Window("Centuś", layout)

# Tymczasowa lista na dzsiejsze zakupy
# dzisiejsze_wpisy = []

while True:
    event, values = window.read()
    
    if event in (sg.WIN_CLOSED, "Wyjście"):
        break

    if event == "Dodaj zakup":
        kat = values['-KAT-']
        kwota_str = values['-KWOTA-'].replace(',', '.')
        try:
            kwota = float(kwota_str)
            db.dodaj_wydatek_db(kat, kwota, uzytkownik="Basia")

            # Resetowanie pola kwoty i potwierdzenie
            window['-KWOTA-'].update('')
            sg.popup_quick_message(f"Zapisano w bazie: {kwota} zł ({kat})", background_color="green", text_color="white")

        except ValueError:
            sg.popup_error("Wpisz poprawną liczbę")

    if event == "Ustawienia":
        # Tworzymy układ nowego okna
        layout_settings = [
            [sg.Text("Zarządzanie kategoriami")],
            [sg.Input(key='-NEW-', size=(20, 1)), sg.Button("Dodaj")],
            [sg.Listbox(values=db.pobierz_kategorie_db(), size=(20, 5), key='-LISTA-')],
            [sg.Button("Ukryj wybraną"), sg.Button("Usuń z bazy"), sg.Button("Zamknij")]
        ]
        win_sett = sg.Window("Ustawienia", layout_settings, modal=True)

        while True:
            e_set, v_set = win_sett.read()
            if e_set in (sg.WIN_CLOSED, "Zamknij"):
                break
            
            if e_set == "Dodaj":
                n_kat = v_set['-NEW-'].strip()
                if n_kat:
                    conn = sqlite3.connect('centus.db') # POPRAWIONA NAZWA
                    c = conn.cursor()

                    # 1. Sprawdzamy, czy taka kategoria już w ogóle istnieje (nawet ukryta)
                    c.execute("SELECT aktywna FROM kategorie WHERE nazwa = ?", (n_kat,))
                    istnieje = c.fetchone()

                    # Jeśli jest ukryta, to ją aktywujemy
                    # c.execute("SELECT aktywna FROM kategorie WHERE nazwa = ?", (n_kat,))
                    # istnieje = c.fetchone()

                    if istnieje:
                        if istnieje[0] == 0:
                            # Jeśli jest ukryta, to ją aktywujemy
                            c.execute("UPDATE kategorie SET aktywna = 1 WHERE nazwa = ?", (n_kat,))
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
                    win_sett['-LISTA-'].update(nowa_lista)
                    window['-KAT-'].update(values=nowa_lista)
                    win_sett['-NEW-'].update('')
                           
                    try:
                        c.execute("INSERT INTO kategorie (nazwa) VALUES (?)", (n_kat,))
                        conn.commit()
                        # Aktualizacja listy w oknie ustawień
                        win_sett['-LISTA-'].update(db.pobierz_kategorie_db())
                        # Aktualizacja Combo w głównym oknie
                        window['-KAT-'].update(values=db.pobierz_kategorie_db())
                        win_sett['-NEW-'].update('')
                    except sqlite3.IntegrityError:
                        sg.popup_error("Już jest taka kategoria!")
                    finally:
                        conn.close() 

            if e_set == "Ukryj wybraną":
                wybrana = v_set['-LISTA-']
                if wybrana:
                    conn = sqlite3.connect('centus.db')
                    c = conn.cursor()
                    c.execute("UPDATE kategorie SET aktywna = 0 WHERE nazwa = ?", (wybrana[0],))
                    conn.commit()
                    conn.close()
                    nowa_lista = db.pobierz_kategorie_db()
                    win_sett['-LISTA-'].update(nowa_lista)
                    window['-KAT-'].update(values=nowa_lista)

            if e_set == "Usuń z bazy":
                wybrana = v_set['-LISTA-']
                if wybrana:
                    odp = sg.popup_yes_no(f"Czy na pewno usunąć '{wybrana[0]}'? Stracisz historię wydatków tej kategorii!")
                    if odp == "Yes":
                        conn = sqlite3.connect('centus.db')
                        c = conn.cursor()
                        c.execute("DELETE FROM kategorie WHERE nazwa = ?", (wybrana[0],))
                        conn.commit()
                        conn.close()
                        nowa_lista = db.pobierz_kategorie_db()
                        win_sett['-LISTA-'].update(nowa_lista)
                        window['-KAT-'].update(values=nowa_lista)

        win_sett.close() 

    if event == " + ":
        nowa = values['-NOWA_KAT-'].strip()
        # db.dodaj_poczatkowe_kategorie_db({nowa}, 1)
        if nowa:
            conn = sqlite3.connect('centus.db')
            kursor = conn.cursor()
            try:
                # 1. NAJPIERW DODAJEMY DO BAZY (tego brakowało!)
                kursor.execute("INSERT INTO kategorie (nazwa, aktywna) VALUES (?, 1)", (nowa,))
                conn.commit()
                # 2. POTEM ODŚWIEŻAMY COMBO (pobieramy nową listę z bazy)
                nowa_lista = db.pobierz_kategorie_db()
                window['-KAT-'].update(values=nowa_lista, value=nowa)
                # 3. CZYŚCIMY POLE WPISYWANIA
                window['-NOWA_KAT-'].update('')
                sg.popup_quick_message(f"Dodano kategorię: {nowa}")
            except sqlite3.IntegrityError:
                sg.popup_error("Taka kategoria już istnieje!")
            finally:
                conn.close()

    if event == "Pokaż wykres skumulowany":
        wm.wydatki_dzienne_skumulowane()

    if event == "Pokaż kategorie":
        kw.wydatki_kategorie()

window.close()

# print([m for m in dir(sg.Combo) if not m.startswith('_')])







