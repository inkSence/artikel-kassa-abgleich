import csv
import os
import json
from datetime import datetime

OUTPUT_ORDNER = "output"
BASIS_DATEINAME = "artikel_vorschlaege.csv"
CONFIG_DATEI = "config.json"

def lese_konfiguration():
    """
    Liest die Konfigurationsdatei ein.
    Gibt ein Dictionary mit den Einstellungen zurück.
    """
    standard_config = {
        "nur_ja_ausgeben": 0,
        "ausschluss_ids": []
    }
    if not os.path.exists(CONFIG_DATEI):
        return standard_config
    
    try:
        with open(CONFIG_DATEI, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Fehler beim Lesen der Konfiguration: {e}")
        return standard_config

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
    Schreibt die gefilterten Daten in eine CSV-Datei mit Zeitstempel im Namen.
    """
    if not daten:
        print("Keine Daten zum Schreiben vorhanden.")
        return

    # Zeitstempel generieren: YYMMDD HHmm
    zeitstempel = datetime.now().strftime("%y%m%d %H%M")
    dateiname = f"{zeitstempel}_{BASIS_DATEINAME}"
    ausgabe_pfad = os.path.join(OUTPUT_ORDNER, dateiname)

    # Sicherstellen, dass das Ausgabeverzeichnis existiert
    os.makedirs(OUTPUT_ORDNER, exist_ok=True)

    feldern = ['Name', 'ID', 'barcode', 'extnr', 'ändern_auf']
    try:
        with open(ausgabe_pfad, mode='w', encoding='utf-8', newline='') as csvdatei:
            writer = csv.DictWriter(csvdatei, fieldnames=feldern, delimiter=';')
            writer.writeheader()
            writer.writerows(daten)
        print(f"Ergebnis erfolgreich in {ausgabe_pfad} geschrieben.")
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
