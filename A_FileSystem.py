import csv
import os
import json
from datetime import datetime

from typing import List, Dict, Any, Optional

OUTPUT_ORDNER = "output"
BASIS_DATEINAME = "artikel_vorschlaege.csv"
CONFIG_DATEI = "config.json"

def lese_konfiguration() -> Dict[str, Any]:
    """
    Liest die Konfigurationsdatei ein.
    Gibt ein Dictionary mit den Einstellungen zurück.
    """
    standard_config: Dict[str, Any] = {
        "nur_ja_ausgeben": 0,
        "ausschluss_ids": [],
        "stückartikel_nicht_ausgeben": 0
    }
    if not os.path.exists(CONFIG_DATEI):
        return standard_config
    
    try:
        with open(CONFIG_DATEI, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Fehler beim Lesen der Konfiguration: {e}")
        return standard_config

def lese_csv_tabelle(dateipfad: str) -> List[Dict[str, str]]:
    """
    Liest eine CSV-Datei mit Semikolon-Trennung ein und gibt sie als Liste von Dictionaries zurück.
    """
    daten: List[Dict[str, str]] = []
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

def schreibe_text_datei(dateipfad: str, inhalt: str) -> None:
    """
    Schreibt einen Text-Inhalt in eine Datei.
    """
    try:
        with open(dateipfad, mode='w', encoding='utf-8') as datei:
            datei.write(inhalt)
    except Exception as e:
        print(f"Fehler beim Schreiben der Datei: {e}")

def schreibe_ergebnis_csv(daten: List[Dict[str, Any]], felder: Optional[List[str]] = None) -> None:
    """
    Schreibt die gefilterten Daten in eine CSV-Datei mit Zeitstempel im Namen.
    Wurden keine Felder übergeben, werden die Keys des ersten Datensatzes verwendet.
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

    if felder is None:
        felder = list(daten[0].keys())

    try:
        with open(ausgabe_pfad, mode='w', encoding='utf-8', newline='') as csvdatei:
            writer = csv.DictWriter(csvdatei, fieldnames=felder, delimiter=';')
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
