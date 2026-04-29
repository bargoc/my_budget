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
            [sg.Button("Ukryj wybraną"), sg.Button("Zamknij")]
        ]
        win_sett = sg.Window("Ustawienia", layout_settings, modal=True)


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







