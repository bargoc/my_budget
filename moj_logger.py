import logging

def skonfiguruj_logger():  # <--- Sprawdź czy tu jest dokładnie taka nazwa
    format_logu = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        filename='DebugInfo.log',
        level=logging.DEBUG,
        format=format_logu,
        encoding='utf-8'
    )
    
    logging.getLogger('matplotlib').setLevel(logging.WARNING)

def pobierz_logger(nazwa_modulu):
    return logging.getLogger(nazwa_modulu)