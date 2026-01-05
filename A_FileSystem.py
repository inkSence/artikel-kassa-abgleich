import csv
import os

OUTPUT_PFAD = "output/artikel_vorschlaege.csv"

def lese_csv_tabelle(dateipfad):
    """
    Liest eine CSV-Datei mit Semikolon-Trennung ein und gibt sie als Liste von Dictionaries zurück.
    """
    daten = []
    if not os.path.exists(dateipfad):
        print(f"Datei nicht gefunden: {dateipfad}")
        return daten

    try:
        with open(dateipfad, mode='r', encoding='utf-8-sig') as csvdatei:
            reader = csv.DictReader(csvdatei, delimiter=';')
            for zeile in reader:
                daten.append(zeile)
    except Exception as e:
        print(f"Fehler beim Lesen der CSV-Datei: {e}")
    
    return daten

def schreibe_text_datei(dateipfad, inhalt):
    """
    Schreibt einen Text-Inhalt in eine Datei.
    """
    try:
        with open(dateipfad, mode='w', encoding='utf-8') as datei:
            datei.write(inhalt)
    except Exception as e:
        print(f"Fehler beim Schreiben der Datei: {e}")

def schreibe_ergebnis_csv(daten):
    """
    Schreibt die gefilterten Daten in die im OUTPUT_PFAD definierte CSV-Datei.
    """
    if not daten:
        print("Keine Daten zum Schreiben vorhanden.")
        return

    # Sicherstellen, dass das Ausgabeverzeichnis existiert
    os.makedirs(os.path.dirname(OUTPUT_PFAD), exist_ok=True)

    feldern = ['Name', 'ID', 'barcode', 'extnr', 'ändern_auf']
    try:
        with open(OUTPUT_PFAD, mode='w', encoding='utf-8', newline='') as csvdatei:
            writer = csv.DictWriter(csvdatei, fieldnames=feldern, delimiter=';')
            writer.writeheader()
            writer.writerows(daten)
        print(f"Ergebnis erfolgreich in {OUTPUT_PFAD} geschrieben.")
    except Exception as e:
        print(f"Fehler beim Schreiben der Ergebnis-CSV: {e}")

if __name__ == "__main__":
    # Test-Code um zu sehen ob es funktioniert
    import glob
    csv_dateien = glob.glob("data/*.csv")
    if csv_dateien:
        test_daten = lese_csv_tabelle(csv_dateien[0])
        print(f"{len(test_daten)} Zeilen eingelesen.")
        if test_daten:
            print("Erste Zeile:", test_daten[0])
