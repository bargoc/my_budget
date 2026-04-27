import matplotlib.pyplot as plt

def wydatki_kategorie():
    categories = ['Jedzenie', 'Dom', 'Auto']
    values = [1200, 2500, 450]

    plt.bar(categories, values)
    plt.title('Wydatki w tym miesiącu wg kategorii')
    plt.show()

wydatki_kategorie()
