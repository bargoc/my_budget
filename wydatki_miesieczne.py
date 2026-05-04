import matplotlib.pyplot as plt
import calendar
from datetime import datetime
import itertools
import db_manager as db

teraz = datetime.now()

# Pobieram aktualną datę
teraz = datetime.now()
rok = teraz.year
miesiac = teraz.month
# monthrange zwraca parę: (dzień tygodnia, liczba dni)
liczba_dni = calendar.monthrange(rok, miesiac)[1]
print(liczba_dni)


# Lista dni od 1 do końca miesiąca
dni_miesiaca = list(range(1, liczba_dni + 1))
print(f"Mamy rok {rok}, miesiąc {miesiac}. Wykres będzie miał {liczba_dni} dni.") 

def wydatki_dzienne_skumulowane():

    # 1. Przykładowe surowe dane (wydatki z konkretnych dni)
    #  Startowe kwoty (czyli 0 zł wydatku rozmieszczone na osi 30 razy)
    surowe_wydatki = [0] * liczba_dni
    print(surowe_wydatki)
    # [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    dane_z_bazy = db.pobierz_wydatki_miesieczne(rok, miesiac)

    for dzien_str, suma in dane_z_bazy:
        indeks = int(dzien_str) - 1
        surowe_wydatki[indeks] = suma

    """ surowe_wydatki[0] = 50   # 1 kwietnia
    surowe_wydatki[26] = 450 # 27 kwietnia (dzisiaj) """

    # Lista skumulowana. itertools.accumulate – "przeniesie" sumę z poprzedniego dnia na następny.
    wszystkie_skumulowane = list(itertools.accumulate(surowe_wydatki))

    # Dni od poczatku miesiąca do dzisiaj
    dzis = teraz.day
     # Bierzemy tylko dni od początku do dzisiaj
    wyswietlane_dni = dni_miesiaca[:dzis]
    wyswietlane_wydatki = wszystkie_skumulowane[:dzis]
    limit_total = db.pobierz_aktualny_limit()

    # Kwoty do wydania rozłożone równomiernie na cały miesiąc
    x_limit = [0, liczba_dni]
    y_limit = [0, limit_total]
    # Wykresy
    plt.bar(wyswietlane_dni, wyswietlane_wydatki, color='skyblue')
    # Linia limitu
    plt.plot(x_limit, y_limit, color='red', linestyle='-', linewidth=1, label='Limit budzetowy')

    plt.xlim(0, liczba_dni + 1)
    plt.ylim(0, max(limit_total, max(wszystkie_skumulowane)) * 1.1) # Skalowanie osi Y
    plt.xlabel("Dzień miesiąca")
    plt.ylabel('Wydatki skumulowane (PLN)')
    plt.title(f'Suma wydatków do dnia: {dzis} {calendar.month_name[miesiac]} {rok}')
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    
    plt.show()

# To, co masz na końcu pliku, schowaj pod tym warunkiem:
if __name__ == "__main__":
    wydatki_dzienne_skumulowane()