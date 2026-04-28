import FreeSimpleGUI as sg
import wydatki_miesieczne as wm
import wydatki_wg_kategorii as kw

sg.theme('SystemDefaultForReal') # Lub np. 'LightBlue'
# Definiujemy listę kategorii (to co ma być w środku listy rozwijanej)
lista_kategorii = ['Zywność', 'Dom', 'Auto', 'Uzywki', "Odziez", "Praca", "Podroze"]

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

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, "Wyjście"):
        break
    if event == "Pokaż wykres skumulowany":
        # Wywołujesz funkcję, którą przed chwilą dopracowałaś
        wm.wydatki_dzienne_skumulowane()


print([m for m in dir(sg.Combo) if not m.startswith('_')])
window.close()






