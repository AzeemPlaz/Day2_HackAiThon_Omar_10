"""EcoTrack entry point."""
from database import initialize_database
from ui.app import EcoTrackApp, ensure_demo_account

if __name__ == "__main__":
    initialize_database()
    ensure_demo_account()
    app = EcoTrackApp()
    app.mainloop()
