# Project Guidelines - Köllektiv Artikel-Synchronisierung

## Project Overview
This project is a tool for the cooperative supermarket **Köllektiv** to synchronize article data from their ERP system (**Lotzapp**) with their POS system (**CasPos**).
The main goal is to identify articles that should be added to or removed from the POS system based on their current inventory levels in Lotzapp.

## Architecture
The project follows a **Clean Architecture** (or Hexagonal Architecture) pattern to ensure separation of concerns and maintainability.

### Folder Structure
- **A_domain**: Contains the core business entities (`Artikel`) and domain-specific logic. It should have no dependencies on other layers.
- **B_application**: Contains the use cases (`ArtikelSyncUseCase`). It coordinates the flow of data and applies business rules.
- **C_adapters**: Bridges the gap between the application logic and the outside world.
    - `cli_controller.py`: Entry point for command-line usage.
    - `web_controller.py`: Entry point for the web-based UI.
    - `artikel_repository.py`: Interface for data access (currently focused on CSV/Config).
- **D_infrastructure**: Concrete implementations of external tools and frameworks.
    - `file_handler.py`: Handles CSV reading and writing.
    - `templates/` & `static/`: Frontend assets for the web mode.
- **Root**:
    - `main.py`: The "Composition Root" that initializes and starts the application.
    - `config.json`: Configuration file for file paths, filters, and operation mode.
    - `data/` & `output/`: Input and output directories for CSV files.

## Technical Details
- **Language**: Python 3.x
- **Web Framework**: Flask (used in `C_adapters/web_controller.py`)
- **Data Format**: CSV (exported from Lotzapp)
- **Configuration**: `config.json` controls the application mode (`local` or `web`) and various filters.

## Guidelines for Junie
- **Maintain Layered Architecture**: Always place new code in the appropriate layer. Do not allow dependencies to point "outwards" (e.g., Domain should not depend on Infrastructure).
- **Domain Logic**: Business rules (like determining if an article's status should change) belong in `A_domain/models.py`.
- **Use Cases**: Orchestration logic belongs in `B_application/use_cases.py`.
- **Coding Style**:
    - Follow existing naming conventions.
    - Use type hints where possible.
    - Domain terms are often in German (e.g., `Lagerstand`, `Kassaartikel`), while architectural terms are in English.
- **Testing**:
    - Currently, there are no automated tests. If you add new logic, consider adding unit tests if possible.
- **Configuration**: Always check `config.json` for configurable parameters instead of hardcoding values.
- **Input/Output**: Be careful with file encodings (the project seems to handle CSVs from Lotzapp).
