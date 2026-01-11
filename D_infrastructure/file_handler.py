import csv
import io
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def lese_json(dateipfad: str) -> Dict[str, Any]:
    """Liest eine JSON-Datei ein."""
    if not os.path.exists(dateipfad):
        return {}
    try:
        with open(dateipfad, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Fehler beim Lesen der JSON-Datei {dateipfad}: {e}")
        return {}

def lese_csv(dateipfad: str, delimiter: str = ';') -> List[Dict[str, str]]:
    """Liest eine CSV-Datei ein."""
    daten: List[Dict[str, str]] = []
    if not os.path.exists(dateipfad):
        return daten
    try:
        with open(dateipfad, mode='r', encoding='utf-8-sig') as csvdatei:
            reader = csv.DictReader(csvdatei, delimiter=delimiter)
            for zeile in reader:
                daten.append(zeile)
    except Exception as e:
        logger.error(f"Fehler beim Lesen der CSV-Datei {dateipfad}: {e}")
    return daten

def parse_csv_string(inhalt: str, delimiter: str = ';') -> List[Dict[str, str]]:
    """Parst einen CSV-String in eine Liste von Dictionaries."""
    daten: List[Dict[str, str]] = []
    try:
        # splitlines() behandelt verschiedene Zeilenenden korrekt
        reader = csv.DictReader(inhalt.splitlines(), delimiter=delimiter)
        for zeile in reader:
            daten.append(zeile)
    except Exception as e:
        logger.error(f"Fehler beim Parsen des CSV-Strings: {e}")
    return daten

def _sanitize_fuer_csv_injection(daten: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Bereinigt Daten, um CSV-Injection (Excel Formula Injection) zu verhindern.
    Werte, die mit gefährlichen Zeichen beginnen, werden mit einem Hochkomma (') escaped.
    """
    gefaehrliche_anfänge = ('=', '+', '-', '@', '\t', '\r')
    bereinigte_daten = []
    for zeile in daten:
        neue_zeile = {}
        for key, wert in zeile.items():
            wert_str = str(wert) if wert is not None else ""
            if wert_str.startswith(gefaehrliche_anfänge):
                neue_zeile[key] = f"'{wert_str}"
            else:
                neue_zeile[key] = wert
        bereinigte_daten.append(neue_zeile)
    return bereinigte_daten

def schreibe_csv(dateipfad: str, daten: List[Dict[str, Any]], felder: List[str], delimiter: str = ';') -> None:
    """Schreibt Daten in eine CSV-Datei."""
    os.makedirs(os.path.dirname(dateipfad), exist_ok=True)
    bereinigte_daten = _sanitize_fuer_csv_injection(daten)
    try:
        with open(dateipfad, mode='w', encoding='utf-8', newline='') as csvdatei:
            writer = csv.DictWriter(csvdatei, fieldnames=felder, delimiter=delimiter)
            writer.writeheader()
            writer.writerows(bereinigte_daten)
    except Exception as e:
        logger.error(f"Fehler beim Schreiben der CSV-Datei {dateipfad}: {e}")

def generiere_csv_string(daten: List[Dict[str, Any]], felder: List[str], delimiter: str = ';') -> str:
    """Generiert einen CSV-String aus Daten."""
    output = io.StringIO()
    bereinigte_daten = _sanitize_fuer_csv_injection(daten)
    try:
        writer = csv.DictWriter(output, fieldnames=felder, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(bereinigte_daten)
    except Exception as e:
        logger.error(f"Fehler beim Generieren des CSV-Strings: {e}")
    return output.getvalue()

def schreibe_text(dateipfad: str, inhalt: str) -> None:
    """Schreibt Text in eine Datei."""
    os.makedirs(os.path.dirname(dateipfad), exist_ok=True)
    try:
        with open(dateipfad, mode='w', encoding='utf-8') as datei:
            datei.write(inhalt)
    except Exception as e:
        logger.error(f"Fehler beim Schreiben der Datei {dateipfad}: {e}")
