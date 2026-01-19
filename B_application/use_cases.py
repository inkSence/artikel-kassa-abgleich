from typing import List, Dict, Any
from A_domain.models import Artikel

class ArtikelSyncUseCase:
    """
    Kapselt den Prozess des Artikelabgleichs zwischen Lagerbestand und Kassasystem.
    Dieser Use Case ist unabhängig von der Datenquelle (CSV, DB, API) und der 
    Ausgabeform (Datei, Web-UI).
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialisiert den Use Case mit den notwendigen Einstellungen.
        """
        self.config = config
        # Vorbereiten der Filter-Einstellungen aus der Config
        self.ausschluss_ids = [str(aid) for aid in config.get("ausschluss_ids", [])]
        self.stueck_filter_aktiv = bool(config.get("stueckartikel_aussortieren", 0))
        self.nur_Änderungen_zu_JA_ausgeben = bool(config.get("nur_Änderungen_zu_JA_ausgeben", 0))

    def execute(self, artikel_liste: List[Artikel]) -> List[Dict[str, Any]]:
        """
        Führt den Abgleich für eine Liste von Artikeln durch.
        Wendet Filter an und nutzt die Domain-Logik der Artikel-Klasse.
        
        Gibt eine Liste von Dictionaries mit den Änderungsvorschlägen zurück.
        """
        ergebnisse = []
        
        for art in artikel_liste:
            # 1. Ausschluss-Filter (IDs auf der Ignorier-Liste)
            if art.id in self.ausschluss_ids:
                continue
            
            # 2. Soll-Status berechnen (Domain Logik aus dem Model)
            soll_status = art.berechne_soll_status()
            if not soll_status:
                # Kein Handlungsbedarf für diesen Artikel
                continue
            
            # 3. Stückartikel-Filter (falls konfiguriert)
            if self.stueck_filter_aktiv and art.einheit == 'Stück':
                continue
            
            # 4. Filter nach 'Nur Ja' (falls konfiguriert)
            if self.nur_Änderungen_zu_JA_ausgeben and soll_status != 'Ja':
                continue
            
            # Mapping der Ergebnisse für die Präsentationsschicht
            ergebnisse.append({
                'Name': art.name,
                'ID': art.id,
                'barcode': art.barcode,
                'extnr': art.extnr,
                'ändern_auf': soll_status,
                'einheit': art.einheit,
                'gruppe': art.gruppe
            })
            
        return ergebnisse
