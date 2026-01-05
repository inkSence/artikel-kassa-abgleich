import A_FileSystem
import B_findArticlesToBeChanged
import glob

def main() -> None:

    print("=== Supermarkt Artikelbestand - Kassenabgleich ===")


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
    stueck_filter_aktiv = bool(config.get("stückartikel_nicht_ausgeben", 0))

    artikel_daten = A_FileSystem.lese_csv_tabelle(neueste_datei)
    
    # 1. Schritt: Nach Kassa-Status und Lagerstand filtern
    treffer_artikel = B_findArticlesToBeChanged.filtere_artikel_nach_inkassa_und_lagerstand(artikel_daten, ausschluss_ids)
    
    # 2. Schritt: Optional Stückartikel ausfiltern
    anzahl_vor_stueck_filter = len(treffer_artikel)
    treffer_artikel = B_findArticlesToBeChanged.filtere_nach_stueckartikel(treffer_artikel, stueck_filter_aktiv)
    
    if stueck_filter_aktiv and len(treffer_artikel) < anzahl_vor_stueck_filter:
        print(f"Filter aktiv: {anzahl_vor_stueck_filter - len(treffer_artikel)} Stückartikel wurden entfernt.")

    # Ggf. weiter filtern basierend auf Konfiguration
    if config.get("nur_ja_ausgeben"):
        print("Filter aktiv: Nur Artikel mit 'ändern_auf: Ja' werden ausgegeben.")
        treffer_artikel = [a for a in treffer_artikel if a['ändern_auf'] == 'Ja']

    # Definition des Datenmodells für die Ausgabe
    ausgabe_daten = []
    ausgabe_felder = ['Name', 'ID', 'barcode', 'extnr', 'ändern_auf']
    
    for a in treffer_artikel:
        ausgabe_daten.append({
            'Name': a.get('name', ''),
            'ID': a.get('ID', ''),
            'barcode': a.get('barcode', ''),
            'extnr': a.get('extnr', ''),
            'ändern_auf': a.get('ändern_auf')
        })

    print(f"{len(ausgabe_daten)} Artikel gefunden, die ausgegeben werden.")

    A_FileSystem.schreibe_ergebnis_csv(ausgabe_daten, ausgabe_felder)
    print("==================================================")

if __name__ == "__main__":
    main()
