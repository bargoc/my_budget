import matplotlib.pyplot as plt
import db_manager as db
from datetime import datetime

def wydatki_kategorie():
    # Pobieramy aktualną datę, by wiedzieć o jaki miesiąc pytać
    dzis = datetime.now()
    rok = dzis.year
    miesiac = dzis.month

    dane = db.pobierz_sumy_kategorii(rok, miesiac)

    if not dane:
        plt.text(0.5, 0.5, 'Brak danych w tym miesiącu, suma -> values')
        plt.show()
        return
    
    # Rozpakowujemy dane: kategoria -> categories, suma -> values
    categories, values = zip(*dane)

    plt.figure(figsize=(6, 6))
    bars = plt.bar(categories, values, color='skyblue')
    
    # Dodajemy etykiety z kwotami nad słupkami
    for bar in bars:
        yval = bar.get_height()
        #plt.text(bar.get_x() + bar.get_width()/2Ś, yval + 5, f'{yval} zł', ha='center', va='bottom')
        plt.text(bar.get_x() + bar.get_width()/2, yval + 5, f'{yval} zł', ha='center', va='bottom')

    plt.title(f'Wydatki wg kategorii - {dzis.strftime("%B %Y")}')
    plt.ylabel('Suma (PLN)')
    plt.xticks(rotation=45) # Pochylenie napisów, jeśli kategorie są długie
    plt.tight_layout() # Żeby napisy nie wyjechały poza ramkę
    plt.show()
""" 
    categories = ['Jedzenie', 'Dom', 'Auto']
    values = [1200, 2500, 450]

    plt.bar(categories, values)
    plt.title('Wydatki w tym miesiącu wg kategorii')
    plt.show() """

if __name__ == "__main__":
    wydatki_kategorie()
