import matplotlib.pyplot as plt
import calendar
from datetime import datetime
import itertools
import db_manager as db
import FreeSimpleGUI as sg


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

def wykres_skumulowany(rok=None, miesiac=None):
    if rok is None or miesiac is None:
        dzis = datetime.now()
        rok, miesiac = dzis.year, dzis.month

    # Pobieramy dane z bazy
    dane_z_db = db.pobierz_sumy_dzienne(rok, miesiac)
    # Pobieramy limit dla danego miesiąca (załóżmy, że masz taką funkcję)
    limit_miesieczny = db.pobierz_limit(rok, miesiac)

    # Wyznaczamy liczbę dni w wybranym miesiącu
    dni_w_miesiacu = calendar.monthrange(rok, miesiac)[1]
    dni = list(range(1, dni_w_miesiacu +1))

    # Przygotowujemy listę wydatków dla każdego dnia (uzupełniamy zera tam, gdzie nie było zakupów)
    wydatki_slownik = {int(dzien): kwota for dzien, kwota in dane_z_db}
    dzienne_kwoty = [wydatki_slownik.get(d, 0) for d in dni]

    # Obliczamy sumę skumulowaną (np. dzień 2 = dzień 1 + dzień 2)
    skumulowane = []
    suma = 0
    for kwota in dzienne_kwoty:
        suma += kwota
        skumulowane.append(suma)

    
    # Rysowanie wykresu
    plt.figure(figsize=(10, 6))
    
    # Słupki wydatków
    plt.bar(dni, skumulowane, color='skyblue', label='Wydatki skumulowane')

    # Linia limitu (czerwona linia prowadząca od 0 do limitu na koniec miesiąca)
    linia_budzetu = [limit_miesieczny * (d / dni_w_miesiacu) for d in dni]
    plt.plot(dni, linia_budzetu, color='red', label='Linia budżetu')

    plt.title(f'Suma wydatków skumulowana: {miesiac:02d}/{rok}')
    plt.xlabel('Dzień miesiąca')
    plt.ylabel('Wydatki (PLN)')
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()


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

    # 3.
    bilans = limit_total - wszystkie_skumulowane[-1]
    print(f"Bilans (limit - wydatki): {bilans} PLN")

    # Kwoty do wydania rozłożone równomiernie na cały miesiąc
    x_limit = [0, liczba_dni]
    y_limit = [0, limit_total]

    
    # 2.
    # DODAWANIE BILANSU NA WYKRES ---
    # Tworzymy tekst
    znak = "+" if bilans >= 0 else ""
    tekst_bilansu = f"Bilans końcowy:\n{znak}{bilans:.2f} zł"
    kolor_tekstu = "green" if bilans >= 0 else "red"
    # Wykresy
    plt.figure(figsize=(7, 6))
    plt.bar(wyswietlane_dni, wyswietlane_wydatki, color='skyblue')
    # Linia limitu
    plt.plot(x_limit, y_limit, color='red', linestyle='-', linewidth=1, label='Limit budzetowy')

    # 1
    # Dodajemy tekst bilansu w prawym górnym rogu wykresu
    plt.text(0.98, 0.07, tekst_bilansu, horizontalalignment='right', verticalalignment='top', transform=plt.gca().transAxes, fontsize=9, color=kolor_tekstu, bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))

    plt.xlim(0, liczba_dni + 1)
    plt.ylim(0, max(limit_total, max(wszystkie_skumulowane)) * 1.1) # Skalowanie osi Y
    plt.xlabel("Dzień miesiąca")
    plt.ylabel('Wydatki skumulowane (PLN)')
    plt.title(f'Suma wydatków do dnia: {dzis} {calendar.month_name[miesiac]} {rok}')
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.show(block=False)

import matplotlib.pyplot as plt

def wykres_roczny(rok):
    # Pobieramy dane z bazy
    dane_z_db = db.pobierz_sumy_miesieczne_w_roku(rok)
    
    if not dane_z_db:
        sg.popup_quick_message(f"Brak jakichkolwiek danych dla roku {rok}", background_color="orange")
        return

    # Polskie nazwy miesięcy na oś X
    nazwy_miesiecy = [
        "Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec",
        "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"
    ]
    
    # Mapujemy dane z bazy (zamieniamy tekstowy numer miesiąca na indeks)
    # dane_z_db ma format np. [('01', 1200.0), ('05', 300.0)]
    wydatki_slownik = {int(miesiac): kwota for miesiac, kwota in dane_z_db}
    
    # Tworzymy pełną listę 12 wartości (jeśli brak miesiąca w bazie, dajemy 0)
    kwoty_miesieczne = [wydatki_slownik.get(i, 0.0) for i in range(1, 13)]

    # Rysowanie wykresu Matplotlib
    plt.figure(figsize=(10, 6))
    
    # Tworzymy słupki
    bars = plt.bar(nazwy_miesiecy, kwoty_miesieczne, color='mediumseagreen', edgecolor='darkgreen')
    
    # Dodajemy wartości nad słupkami, żeby wykres był czytelniejszy
    for bar in bars:
        yval = bar.get_height()
        if yval > 0: # Pokazujemy etykietę tylko, jeśli wydatek jest większy od zera
            plt.text(bar.get_x() + bar.get_width()/2, yval + 10, f"{int(yval)} zł", ha='center', va='bottom', fontsize=9)

    plt.title(f'Podsumowanie wydatków za rok: {rok}', fontsize=14, fontweight='bold')
    plt.xlabel('Miesiąc')
    plt.ylabel('Suma wydatków (PLN)')
    plt.xticks(rotation=30) # Lekkie obrócenie nazw, żeby się nie nakładały
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout() # Zapobiega obcinaniu podpisów na macOS
    plt.show()
    

# To, co masz na końcu pliku, schowaj pod tym warunkiem:
if __name__ == "__main__":
    wydatki_dzienne_skumulowane()