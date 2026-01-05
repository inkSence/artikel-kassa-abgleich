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

    artikel_daten = A_FileSystem.lese_csv_tabelle(neueste_datei)
    gefilterte_artikel = B_findArticlesToBeChanged.filtere_artikel_nach_inkassa_und_lagerstand(artikel_daten, ausschluss_ids)

    # Ggf. weiter filtern basierend auf Konfiguration
    if config.get("nur_ja_ausgeben"):
        print("Filter aktiv: Nur Artikel mit 'ändern_auf: Ja' werden ausgegeben.")
        gefilterte_artikel = [a for a in gefilterte_artikel if a['ändern_auf'] == 'Ja']

    print(f"{len(gefilterte_artikel)} Artikel gefunden, die ausgegeben werden.")

    A_FileSystem.schreibe_ergebnis_csv(gefilterte_artikel)
    print("==================================================")

if __name__ == "__main__":
    main()
