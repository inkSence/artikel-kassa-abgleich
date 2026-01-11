from C_adapters.cli_controller import CLIController
from C_adapters import artikel_repository
from A_domain.models import AppMode

def main() -> None:
    """
    Einstiegspunkt der Anwendung (Composition Root).
    Hier wird entschieden, welcher Controller (CLI, Web, etc.) gestartet wird.
    """
    config = artikel_repository.lade_konfiguration()
    mode_str = config.get("mode", "local")
    
    try:
        # Hier nutzen wir das Enum, um sicherzustellen, dass nur erlaubte Werte verarbeitet werden
        mode = AppMode(mode_str)
    except ValueError:
        print(f"Fehler: Ungueltiger Modus '{mode_str}' in der Konfiguration.")
        print(f"Erlaubte Werte sind: {[m.value for m in AppMode]}")
        return

    if mode == AppMode.LOCAL:
        controller = CLIController()
        controller.execute()
    elif mode == AppMode.WEB:
        from C_adapters.web_controller import run
        print("Starte Web-Modus auf Port 8000...")
        run()
    else:
        print(f"Der Modus {mode} wird aktuell nicht unterstuetzt.")

if __name__ == "__main__":
    main()
