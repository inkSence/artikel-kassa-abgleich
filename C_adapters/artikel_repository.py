import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from A_domain.models import Artikel
from D_infrastructure import file_handler

CONFIG_DATEI = "config.json"
OUTPUT_ORDNER = "output"
BASIS_DATEINAME = "vorschlaege_IN_KASSA.csv"

def lade_konfiguration() -> Dict[str, Any]:
    """Lädt die Konfiguration und stellt Standardwerte bereit."""
    config = file_handler.lese_json(CONFIG_DATEI)
    standard_config = {
        "mode": "local",
        "nur_Änderungen_zu_JA_ausgeben": 0,
        "ausschluss_ids": [],
        "stueckartikel_aussortieren": 0,
        "postfix_outputdatei_web": "vorschlaege_IN_KASSA"
    }
    # Mergen mit Standardwerten
    for key, value in standard_config.items():
        if key not in config:
            config[key] = value
    return config

def lade_artikel_aus_csv(dateipfad: str) -> List[Artikel]:
    """Lädt Rohdaten und mappt sie auf Artikel-Entities."""
    rohdaten = file_handler.lese_csv(dateipfad)
    return _map_csv_daten_zu_artikel_liste(rohdaten)

def lade_artikel_aus_string(inhalt: str) -> List[Artikel]:
    """Parst CSV-Inhalt aus einem String und mappt ihn auf Artikel-Entities."""
    rohdaten = file_handler.parse_csv_string(inhalt)
    return _map_csv_daten_zu_artikel_liste(rohdaten)

def exportiere_ergebnisse(ergebnisse: List[Dict[str, Any]], felder: List[str]) -> None:
    """Bereitet den Exportpfad vor und schreibt die CSV."""
    if not ergebnisse:
        return

    zeitstempel = datetime.now().strftime("%y%m%d %H%M")
    dateiname = f"{zeitstempel}_{BASIS_DATEINAME}"
    ausgabe_pfad = os.path.join(OUTPUT_ORDNER, dateiname)
    
    file_handler.schreibe_csv(ausgabe_pfad, ergebnisse, felder)
    print(f"Ergebnis erfolgreich in {ausgabe_pfad} geschrieben.")

def erzeuge_export_string(ergebnisse: List[Dict[str, Any]], felder: List[str]) -> str:
    """Erzeugt einen CSV-String für den Export."""
    return file_handler.generiere_csv_string(ergebnisse, felder)

def _map_csv_daten_zu_artikel_liste(daten: List[Dict[str, str]]) -> List[Artikel]:
    """Interner Mapper: CSV-Dict -> Artikel Entity."""
    artikel_liste = []
    for zeile in daten:
        try:
            ls_str = str(zeile.get('lagerstand', '0')).replace(',', '.')
            lagerstand = float(ls_str)
            ist_kassa = str(zeile.get('kassaartikel')) == '1'
            
            artikel = Artikel(
                id=str(zeile.get('ID', '')),
                name=zeile.get('name', ''),
                lagerstand=lagerstand,
                ist_kassaartikel=ist_kassa,
                einheit=zeile.get('einheit', ''),
                barcode=zeile.get('barcode', ''),
                extnr=zeile.get('extnr', '')
            )
            artikel_liste.append(artikel)
        except (ValueError, TypeError) as e:
            print(f"Warnung: Fehler beim Mapping von Artikel ID {zeile.get('ID')}: {e}")
            continue
    return artikel_liste
