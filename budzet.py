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
    [sg.Text("Budżet Domowy", font=("Arial", 20))], 
    [sg.Text("Wybierz kategorię:")], 
    [sg.Combo(lista_kategorii, key='-KAT-', readonly=True, default_value=lista_kategorii[0], size=(21, 1))], 
    [sg.Text("Dodaj nową kategorię:")],
    [sg.Input(key='-NOWA_KAT-', size=(23, 1)), sg.Button(" + ")],
    [sg.Text("Kwota:")],
    [sg.Input(key='-KWOTA-', size=(23, 1))],
    
    # NOWY PRZYCISK: Akceptacja pojedynczego zakupu
    [sg.Button("Dodaj zakup", bind_return_key=True, button_color=('white', 'green'), size=(22, 1))],
    
    [sg.HorizontalSeparator()], # Estetyczna linia oddzielająca
    [sg.Button("Pokaż wykres skumulowany", size=(22, 1))],
    [sg.Button("Pokaż kategorie", size=(22, 1))],
    [sg.Button("Wyjście", size=(22, 1))]
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

    if event == " + ":
        nowa = values['-NOWA_KAT-'].strip()
        if nowa:
            conn = sqlite3.connect('centus_db')
            kursor = conn.cursor()
            try:
                # Combo pobiera kategorie z bazy
                nowa_lista = db.pobierz_kategorie_db()
                window['-KAT-'].update(values=nowa_lista, value=nowa)
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







