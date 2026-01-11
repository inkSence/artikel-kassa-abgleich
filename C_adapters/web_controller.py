from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import io
import os
from C_adapters import artikel_repository
from B_application.use_cases import ArtikelSyncUseCase

app = FastAPI(title="Artikel Kassenabgleich API")

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
async def process_csv_api(file: UploadFile = File(...)):
    """Endpunkt zum Verarbeiten einer CSV, gibt JSON für die UI zurück."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Nur CSV-Dateien sind erlaubt.")

    try:
        inhalt = await file.read()
        inhalt_str = inhalt.decode("utf-8-sig")
        config = artikel_repository.lade_konfiguration()
        artikel_objekte = artikel_repository.lade_artikel_aus_string(inhalt_str)
        
        if not artikel_objekte:
            raise HTTPException(status_code=400, detail="Keine gültigen Artikeldaten gefunden.")

        use_case = ArtikelSyncUseCase(config)
        ergebnisse = use_case.execute(artikel_objekte)
        
        return {"filename": file.filename, "results": ergebnisse}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Endpunkt zum Hochladen einer CSV und Erhalten der Ergebnisse."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Nur CSV-Dateien sind erlaubt.")

    try:
        # 1. Datei einlesen
        inhalt = await file.read()
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
        original_name = os.path.splitext(file.filename)[0]
        postfix = config.get("postfix_outputdatei_web", "vorschlaege_IN_KASSA")
        download_filename = f"{original_name}{postfix}.csv"

        # 6. Als Download zurückgeben
        output = io.StringIO(csv_export)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={download_filename}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interner Fehler: {str(e)}")

def run():
    """Startet den Webserver."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
