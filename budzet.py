import FreeSimpleGUI as sg
import wydatki_miesieczne as wm
import wydatki_wg_kategorii as kw

sg.theme('SystemDefaultForReal') # Lub np. 'LightBlue'
# Definiujemy listę kategorii (to co ma być w środku listy rozwijanej)
lista_kategorii = ['Wydatek bez kategorii', 'Żywność', 'Dom', 'Auto', 'Używki', "Odzież", "Praca", "Podroże"]

layout = [
    [sg.Text("Budżet Domowy", font=("Arial", 20))], 
    [sg.Text("Wybierz kategorię:")], 
    [sg.Combo(lista_kategorii, key='-KAT-', readonly=True, default_value='Zywność', size=(21, 1))], 
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
dzisiejsze_wpisy = []

while True:
    event, values = window.read()
    
    if event in (sg.WIN_CLOSED, "Wyjście"):
        break

    if event == "Dodaj zakup":
        kat = values['-KAT-']
        kwota = values['-KWOTA-']
        
        if kwota.replace('.', '', 1).isdigit(): # Proste sprawdzenie czy to liczba
            dzisiejsze_wpisy.append((kat, float(kwota)))
            print(f"Dodano: {kat} - {kwota} PLN") # Zobaczysz to w terminalu VS Code
            
            # CZYSZCZENIE: Resetujemy pole kwoty, ale zostawiamy kategorię
            window['-KWOTA-'].update('')
            sg.popup_quick_message(f"Zapisano {kwota} zł do kategorii {kat}", background_color='green', text_color='white')
        else:
            sg.popup_error("Błąd: Wpisz poprawną kwotę (użyj kropki zamiast przecinka)!")

    if event == "Pokaż wykres skumulowany":
        wm.wydatki_dzienne_skumulowane()

    if event == "Pokaż kategorie":
        kw.wydatki_kategorie()

window.close()

# print([m for m in dir(sg.Combo) if not m.startswith('_')])







