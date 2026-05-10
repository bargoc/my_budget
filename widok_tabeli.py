import FreeSimpleGUI as sg
from datetime import datetime
import db_manager as db  # Musisz zaimportować db_manager tutaj

def okno_listy_wydatkow():
    dzis = datetime.now()
    dane = db.pobierz_liste_wydatkow(dzis.year, dzis.month)

    naglowki = ["Data", "Kategoria", "Kwota (zł)"]

    layout_tabeli = [
        [sg.Text(f"Przegląd wydatków: {dzis.strftime('%m/%Y')}", font=('Helvetica', 14, 'bold'))],
        [sg.Table(values=dane, 
                  headings=naglowki, 
                  auto_size_columns=True, 
                  justification='left', 
                  num_rows=min(len(dane), 20) if dane else 10, 
                  key='-TABELA_LISTA-', 
                  row_height=25, 
                  alternating_row_color='lightgray')],
        [sg.Button("Zamknij")]
    ]

    window = sg.Window("Lista wydatków", layout_tabeli, modal=True, finalize=True)

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Zamknij"):
            break
    window.close()