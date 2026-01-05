

def filtere_artikel(daten, ausschluss_ids=None):
    """
    Filtert die Artikel basierend auf Lagerstand und Kassaartikel-Status.
    Gibt eine Liste von Dictionaries mit den gewünschten Spalten zurück.
    """
    if ausschluss_ids is None:
        ausschluss_ids = []
        
    ergebnisse = []
    
    for zeile in daten:
        try:
            artikel_id = zeile.get('ID', '')
            
            # Prüfen, ob die ID auf der Ausschlussliste steht
            if artikel_id in ausschluss_ids:
                continue
                
            # Lagerstand konvertieren (Komma zu Punkt für float)
            lagerstand_str = zeile.get('lagerstand', '0').replace(',', '.')
            lagerstand = float(lagerstand_str)
            
            kassaartikel = zeile.get('kassaartikel', '0')
            
            andern_auf = None
            
            # Logik:
            # 1. Bestand > 0 und kassaartikel == 0 -> ändern auf Ja
            if lagerstand > 0 and kassaartikel == '0':
                andern_auf = 'Ja'
            
            # 2. Bestand <= 0 und kassaartikel == 1 -> ändern auf Nein
            elif lagerstand <= 0 and kassaartikel == '1':
                andern_auf = 'Nein'
                
            if andern_auf:
                ergebnisse.append({
                    'Name': zeile.get('name', ''),
                    'ID': zeile.get('ID', ''),
                    'barcode': zeile.get('barcode', ''),
                    'extnr': zeile.get('extnr', ''),
                    'ändern_auf': andern_auf
                })
        except ValueError:
            print(f"Warnung: Konnte Lagerstand für Artikel ID {zeile.get('ID')} nicht lesen: {zeile.get('lagerstand')}")
            
    return ergebnisse

