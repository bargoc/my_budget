import FreeSimpleGUI as sg
import wydatki_miesieczne as wm
import wydatki_wg_kategorii as kw

sg.theme('SystemDefaultForReal') # Lub np. 'LightBlue'
# Definiujemy listę kategorii (to co ma być w środku listy rozwijanej)
lista_kategorii = ['Zywność', 'Dom', 'Auto', 'Uzywki', "Odziez", "Praca", "Podroze"]

layout = [
    [sg.Text("Budżet Domowy", font=("Arial", 20))], 
    [sg.Text("Wybierz kategorię:")], 
    [sg.Combo(lista_kategorii, key='-KAT-', readonly=True, default_value='Zywność')], 
    [sg.Text("Kwota:"), sg.Input(key='-KWOTA-', size=(10, 1))],
    
    # NOWY PRZYCISK: Akceptacja pojedynczego zakupu
    [sg.Button("Dodaj zakup", bind_return_key=True, button_color=('white', 'green'))],
    
    [sg.HorizontalSeparator()], # Estetyczna linia oddzielająca
    [sg.Button("Pokaż wykres skumulowany")],
    [sg.Button("Pokaż kategorie")],
    [sg.Button("Wyjście")]
]

window = sg.Window("Centuś", layout)

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, "Wyjście"):
        break
    if event == "Pokaż wykres skumulowany":
        # Wywołujesz funkcję, którą przed chwilą dopracowałaś
        wm.wydatki_dzienne_skumulowane()

window.close()

