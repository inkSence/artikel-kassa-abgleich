import glob
from C_adapters import artikel_repository
from B_application.use_cases import ArtikelSyncUseCase
from A_domain.models import KassaartikelMissingException

class CLIController:
    """
    Dieser Controller ist der Adapter für die Kommandozeilen-Schnittstelle (CLI).
    Er kümmert sich um die Auswahl der lokalen Dateien und die Konsolen-Ausgabe.
    """
    
    def execute(self):
        print("=== Supermarkt Artikelbestand - Kassenabgleich (CLI-Controller) ===")
        
        try:
            # 1. Datei suchen (Infrastruktur-Detail, hier noch im Controller)
            csv_dateien = glob.glob("data/*.csv")
            if not csv_dateien:
                print("Keine CSV-Dateien im Ordner 'data/' gefunden.")
                return

            neueste_datei = sorted(csv_dateien)[-1]
            print(f"Verarbeite Datei: {neueste_datei}")

            # 2. Daten laden über das Repository (Adapter Layer)
            config = artikel_repository.lade_konfiguration()
            artikel_objekte = artikel_repository.lade_artikel_aus_csv(neueste_datei)
            
            # 3. Business Logik über den Use Case ausführen
            use_case = ArtikelSyncUseCase(config)
            ergebnisse = use_case.execute(artikel_objekte)

            # 4. Ergebnis-Ausgabe über das Repository
            print(f"{len(ergebnisse)} Artikel gefunden, die für den Export vorbereitet wurden.")
            
            ausgabe_felder = ['Name', 'ID', 'barcode', 'extnr', 'ändern_auf', 'einheit']
            artikel_repository.exportiere_ergebnisse(ergebnisse, ausgabe_felder)
        except KassaartikelMissingException as e:
            print(f"FEHLER: {e}")
        except Exception as e:
            print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
        
        print("==================================================")
