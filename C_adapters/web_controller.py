from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import io
import os
import logging
from C_adapters import artikel_repository
from B_application.use_cases import ArtikelSyncUseCase

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Artikel Kassenabgleich API")

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

# Pfade für Templates und Statische Dateien konfigurieren
basis_pfad = os.path.dirname(os.path.dirname(__file__))
template_pfad = os.path.join(basis_pfad, "D_infrastructure", "templates")
static_pfad = os.path.join(basis_pfad, "D_infrastructure", "static")

# Statische Dateien mounten (CSS, Bilder, etc.)
app.mount("/static", StaticFiles(directory=static_pfad), name="static")

templates = Jinja2Templates(directory=template_pfad)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Zeigt die Startseite mit Upload-Formular via Jinja2 Template."""
    config = artikel_repository.lade_konfiguration()
    return templates.TemplateResponse("index.html", {"request": request, "config": config})

@app.post("/api/process")
async def process_csv_api(
    file: UploadFile = File(...),
    nur_ja: bool = Form(False),
    stueck_aus: bool = Form(False)
):
    """Endpunkt zum Verarbeiten einer CSV, gibt JSON für die UI zurück."""
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="Nur CSV-Dateien sind erlaubt.")

    # Prüfung der Dateigröße
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Datei ist zu groß. Maximal 5 MB erlaubt.")

    try:
        inhalt = await file.read()
        
        # Sicherheitscheck: Falls file.size None war, hier nach dem Lesen prüfen
        if len(inhalt) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="Datei ist zu groß. Maximal 5 MB erlaubt.")
            
        inhalt_str = inhalt.decode("utf-8-sig")
        
        # Basis-Konfiguration laden und mit Web-Eingaben überschreiben
        config = artikel_repository.lade_konfiguration()
        config["nur_Änderungen_zu_JA_ausgeben"] = 1 if nur_ja else 0
        config["stueckartikel_aussortieren"] = 1 if stueck_aus else 0

        artikel_objekte = artikel_repository.lade_artikel_aus_string(inhalt_str)
        
        if not artikel_objekte:
            raise HTTPException(status_code=400, detail="Keine gültigen Artikeldaten gefunden.")

        use_case = ArtikelSyncUseCase(config)
        ergebnisse = use_case.execute(artikel_objekte)
        
        # Dateiname für die UI säubern
        safe_filename = os.path.basename(file.filename)
        
        return {"filename": safe_filename, "results": ergebnisse}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler in process_csv_api: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Bei der Verarbeitung der Daten ist ein interner Fehler aufgetreten.")

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Endpunkt zum Hochladen einer CSV und Erhalten der Ergebnisse."""
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="Nur CSV-Dateien sind erlaubt.")

    # Prüfung der Dateigröße
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Datei ist zu groß. Maximal 5 MB erlaubt.")

    try:
        # 1. Datei einlesen
        inhalt = await file.read()
        
        # Sicherheitscheck: Falls file.size None war, hier nach dem Lesen prüfen
        if len(inhalt) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="Datei ist zu groß. Maximal 5 MB erlaubt.")
            
        inhalt_str = inhalt.decode("utf-8-sig") # utf-8-sig für BOM Handling

        # 2. Konfiguration laden
        config = artikel_repository.lade_konfiguration()

        # 3. Daten in Domain-Objekte mappen
        artikel_objekte = artikel_repository.lade_artikel_aus_string(inhalt_str)
        
        if not artikel_objekte:
            raise HTTPException(status_code=400, detail="Keine gültigen Artikeldaten in der Datei gefunden.")

        # 4. Use Case ausführen
        use_case = ArtikelSyncUseCase(config)
        ergebnisse = use_case.execute(artikel_objekte)

        # 5. Export-String generieren
        ausgabe_felder = ['Name', 'ID', 'barcode', 'extnr', 'ändern_auf', 'einheit']
        csv_export = artikel_repository.erzeuge_export_string(ergebnisse, ausgabe_felder)

        # Dateiname für den Download vorbereiten (Postfix aus Config vor der Endung)
        safe_filename = os.path.basename(file.filename)
        original_name = os.path.splitext(safe_filename)[0]
        postfix = config.get("postfix_outputdatei_web", "vorschlaege_IN_KASSA")
        download_filename = f"{original_name}{postfix}.csv"

        # 6. Als Download zurückgeben
        output = io.StringIO(csv_export)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={download_filename}"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler in upload_csv: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Bei der Verarbeitung der Datei ist ein interner Fehler aufgetreten.")

def run():
    """Startet den Webserver."""
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
