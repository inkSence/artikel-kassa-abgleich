from dataclasses import dataclass
from typing import Optional
from enum import Enum


class AppMode(Enum):
    LOCAL = "local"
    WEB = "web"


@dataclass
class Artikel:
    id: str
    name: str
    lagerstand: float
    ist_kassaartikel: bool
    einheit: str
    barcode: str = ""
    extnr: str = ""

    def berechne_soll_status(self) -> Optional[str]:
        """
        Berechnet, ob der Status des Artikels in der Kassa geändert werden muss.
        Gibt 'Ja', 'Nein' oder None zurück.
        """
        # 1. Bestand > 0 und kassaartikel == 0 -> ändern auf Ja
        if self.lagerstand > 0 and not self.ist_kassaartikel:
            return "Ja"
        
        # 2. Bestand <= 0 und kassaartikel == 1 -> ändern auf Nein
        if self.lagerstand <= 0 and self.ist_kassaartikel:
            return "Nein"
            
        return None