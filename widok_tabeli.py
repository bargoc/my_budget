import FreeSimpleGUI as sg
from datetime import datetime
import db_manager as db  # Musisz zaimportować db_manager tutaj

def okno_listy_wydatkow():
    dzis = datetime.now()
    
    def odswiez_dane():
        return db.pobierz_liste_wydatkow(dzis.year, dzis.month)
    
    dane = odswiez_dane()
    naglowki = ["ID", "Data", "Kategoria", "Kwota (zł)"] # ID jest na indeksie 0

    layout_tabeli = [
        [sg.Text(f"Przegląd wydatków: {dzis.strftime('%m/%Y')}", font=('Helvetica', 14, 'bold'))],
        [sg.Table(values=dane, 
                  headings=naglowki, 
                  auto_size_columns=True, 
                  num_rows=15,
                  # justification='left', 
                  # num_rows=min(len(dane), 20) if dane else 10, 
                  key='-TABELA_LISTA-', 
                  row_height=25, 
                  # Tabela nadal "trzyma" dane o ID w pamięci (pod indeksem 0), ale nie widzimy go.
                  visible_column_map=[False, True, True, True],
                  display_row_numbers=False,
                  # Zapobiega zaznaczeniu wielu wierszy naraz. Uproszczenie obsługi błędów – 
                  # jeden klik to jeden konkretny wydatek do usunięcia.
                  select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                  alternating_row_color='lightgray')],
        [sg.Button("Usuń wybrany", button_color=('white', 'red')), sg.Push(), sg.Button("Zamknij")]
    ]

    window = sg.Window("Lista wydatków", layout_tabeli, modal=True, finalize=True)

    while True:
        event, values = window.read()
                
        if event in (sg.WIN_CLOSED, "Zamknij"):
            break

        if event == "Usuń wybrany":
            # values['-TABELA_LISTA-'] zwraca listę indeksów zaznaczonych wierszy
            wybrane_indeksy = values['-TABELA_LISTA-']

            if wybrane_indeksy:
                indeks = wybrane_indeksy[0]
                # Pobieramy ID z naszych danych
                id_do_usuniecia = dane[indeks][0]

                # Potwierdzenie usunięcia (bezpieczniej dla użytkownika)
                if sg.popup_yes_no("Czy na pewno chcesz usunąć ten wydatek?", title="Potwierdzenie") == "Yes":
                    db.usun_wydatek(id_do_usuniecia)
                    # Odświeżamy widok
                    dane = odswiez_dane()
                    # dane = db.pobierz_liste_wydatkow()
                    window['-TABELA_LISTA-'].update(values=dane)
                    sg.popup_quick_message("Wydatek usunięty.", background_color="red")
                else:
                    sg.popup_error("Zaznacz wydatek, który chcesz usunąć.")
    window.close()

