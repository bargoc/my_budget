import matplotlib.pyplot as plt
import calendar
from datetime import datetime
import itertools

teraz = datetime.now()

# Pobieram aktualną datę
teraz = datetime.now()
rok = teraz.year
miesiac = teraz.month
liczba_dni = calendar.monthrange(rok, miesiac)[1]


# Lista dni od 1 do końca miesiąca
dni_miesiaca = list(range(1, liczba_dni + 1))
print(f"Mamy rok {rok}, miesiąc {miesiac}. Wykres będzie miał {liczba_dni} dni.") 

def wydatki_dzienne_skumulowane():

    # 1. Przykładowe surowe dane (wydatki z konkretnych dni)
    surowe_wydatki = [0] * liczba_dni
    surowe_wydatki[0] = 50   # 1 kwietnia
    surowe_wydatki[1] = 100  # 2 kwietnia
    surowe_wydatki[2] = 80   # 3 kwietnia
    surowe_wydatki[26] = 450 # 27 kwietnia (dzisiaj)

    # Lista skumulowana
    wszystkie_skumulowane = list(itertools.accumulate(surowe_wydatki))

    # Dni od poczatku miesiąca do dzisiaj
    dzis = teraz.day
    wyswietlane_dni = dni_miesiaca[:dzis]
    wyswietlane_wydatki = wszystkie_skumulowane[:dzis]

    # Wykres
    plt.bar(wyswietlane_dni, wyswietlane_wydatki, color='skyblue')
    plt.xlim(0, liczba_dni + 1)
    plt.xlabel("Dzień miesiąca")
    plt.ylabel("Wydatki skumulowane {PLN)}")
    plt.title(f'Suma wydatków do dnia: {dzis} {calendar.month_name[miesiac]}')

    plt.plot(ypoints, linestyle = 'dotted')
    plt.show()

wydatki_dzienne_skumulowane()
 


