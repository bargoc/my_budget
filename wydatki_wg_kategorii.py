import matplotlib.pyplot as plt
import db_manager as db
from datetime import datetime
import FreeSimpleGUI as sg

def wydatki_kategorie(rok=None, miesiac=None):
    # Pobieramy aktualną datę, by wiedzieć o jaki miesiąc pytać
    # dzis = datetime.now()
    # rok = dzis.year
    # miesiac = dzis.month
    if rok is None or miesiac is None:
        dzis = datetime.now()
        rok, miesiac = dzis.year, dzis.month
    else:
        # Tworzymy obiekt daty tylko dla potrzeb tytułu wykresu
        dzis = datetime(rok, miesiac, 1) 

    dane = db.pobierz_sumy_kategorii(rok, miesiac)

    if not dane:
        sg.popup_quick_message(f"Brak danych dla okresu {miesiac}/{rok}")
        return

    if not dane:
        # plt.text(0.5, 0.5, 'Brak danych w tym miesiącu, suma -> values')
        plt.text(0.5, 0.5, 'Brak danych w tym miesiącu', 
                 horizontalalignment='center', 
                 verticalalignment='center', 
                 fontsize=9, 
                 color='gray',
                 transform=plt.gca().transAxes)
        plt.show()
        return
    
    # Rozpakowujemy dane: kategoria -> categories, suma -> values
    categories, values = zip(*dane)
    # Możesz ustawić rozmiar wykresu w matplotlib, żeby był szerszy: np. Szerokość 7 cali, wysokość 6
    plt.figure(figsize=(6, 5))
    bars = plt.bar(categories, values, color='skyblue')
    
    # Dodajemy etykiety z kwotami nad słupkami
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 1, f'{yval} zł', ha='center', va='bottom')

    plt.title(f'Wydatki wg kategorii - {dzis.strftime("%B %Y")}')
    plt.ylabel('Suma (PLN)')
    plt.xticks(rotation=45) # Pochylenie napisów, jeśli kategorie są długie
    plt.tight_layout() # Żeby napisy nie wyjechały poza ramkę
    plt.show()

if __name__ == "__main__":
    wydatki_kategorie()
