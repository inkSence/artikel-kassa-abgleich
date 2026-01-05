import A_FileSystem
import csv
import os
import glob

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

def haupt_prozess():
    """
    Führt den gesamten Prozess der Artikelfilterung aus:
    Datei suchen, einlesen, filtern und Ergebnis schreiben.
    """
    # Suche nach der aktuellsten CSV-Datei im data Ordner
    csv_dateien = glob.glob("data/*.csv")
    if not csv_dateien:
        print("Keine CSV-Dateien im Ordner 'data/' gefunden.")
        return
    
    # Sortieren, um die neueste Datei zu bekommen (basierend auf dem Zeitstempel im Namen)
    neueste_datei = sorted(csv_dateien)[-1]
    print(f"Verarbeite Datei: {neueste_datei}")
    
    # Konfiguration laden
    config = A_FileSystem.lese_konfiguration()
    ausschluss_ids = config.get("ausschluss_ids", [])
    
    artikel_daten = A_FileSystem.lese_csv_tabelle(neueste_datei)
    gefilterte_artikel = filtere_artikel(artikel_daten, ausschluss_ids)
    
    # Ggf. weiter filtern basierend auf Konfiguration
    if config.get("nur_ja_ausgeben"):
        print("Filter aktiv: Nur Artikel mit 'ändern_auf: Ja' werden ausgegeben.")
        gefilterte_artikel = [a for a in gefilterte_artikel if a['ändern_auf'] == 'Ja']
    
    print(f"{len(gefilterte_artikel)} Artikel gefunden, die ausgegeben werden.")
    
    A_FileSystem.schreibe_ergebnis_csv(gefilterte_artikel)

if __name__ == "__main__":
    haupt_prozess()
