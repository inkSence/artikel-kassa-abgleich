

from typing import List, Dict, Any, Optional

def filtere_artikel_nach_inkassa_und_lagerstand(daten: List[Dict[str, str]], ausschluss_ids: Optional[List[Any]] = None) -> List[Dict[str, str]]:
    """
    Filtert die Artikel basierend auf Lagerstand und Kassaartikel-Status.
    Gibt eine Liste von Dictionaries zurück, wobei jeder gefundene Artikel um das Feld 'ändern_auf' erweitert wurde.
    """
    if ausschluss_ids is None:
        ausschluss_ids = []
    else:
        # Sicherstellen, dass alle IDs als Strings verglichen werden
        ausschluss_ids = [str(aid) for aid in ausschluss_ids]
        
    ergebnisse: List[Dict[str, str]] = []
    
    for zeile in daten:
        try:
            artikel_id = zeile.get('ID', '')
            
            # Prüfen, ob die ID auf der Ausschlussliste steht
            if artikel_id in ausschluss_ids:
                continue
            
            # Lagerstand konvertieren (Komma zu Punkt für float)
            lagerstand_val = zeile.get('lagerstand', '0')
            if isinstance(lagerstand_val, str):
                lagerstand_str = lagerstand_val.replace(',', '.')
            else:
                lagerstand_str = str(lagerstand_val)
                
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
                # Kopie erstellen und markieren
                artikel_treffer = zeile.copy()
                artikel_treffer['ändern_auf'] = andern_auf
                ergebnisse.append(artikel_treffer)
        except ValueError:
            print(f"Warnung: Konnte Lagerstand für Artikel ID {zeile.get('ID')} nicht lesen: {zeile.get('lagerstand')}")
            
    return ergebnisse

def filtere_nach_stueckartikel(daten: List[Dict[str, str]], aktiv: bool = False) -> List[Dict[str, str]]:
    """
    Filtert Artikel heraus, deren einheit 'Stück' ist, falls aktiv True ist.
    """
    if not aktiv:
        return daten
    
    return [a for a in daten if a.get('einheit') != 'Stück']

if __name__ == "__main__":
    # Ermöglicht das Testen des Moduls
    print("B_findArticlesToBeChanged: Modul-Test")
    test_daten = [
        {'name': 'Test1', 'ID': '1', 'lagerstand': '5,0', 'kassaartikel': '0'},
        {'name': 'Test2', 'ID': '2', 'lagerstand': '0,0', 'kassaartikel': '1'}
    ]
    ergebnis = filtere_artikel_nach_inkassa_und_lagerstand(test_daten)
    print(f"Testergebnis: {ergebnis}")

