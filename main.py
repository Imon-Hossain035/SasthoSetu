"""SasthoSetu - AI-Assisted Triage System for Rural Telemedicine Access.

Entry point for the SasthoSetu Windows Desktop Application.
Current Stage: Step 22 (Final University Submission Preparation)
"""

import sys
import traceback
from utils.logger import setup_logger, get_logger


def main() -> None:
    """Initializes and runs the SasthoSetu desktop application."""
    # 1. Initialize Application Logger
    setup_logger()
    log = get_logger("main")

    print("=" * 60)
    print("  SasthoSetu (স্বাস্থ্যসেতু) Desktop Application")
    print("  AI-Assisted Triage for Rural Telemedicine")
    print("=" * 60)
    print("\n[INFO] Starting SasthoSetu Desktop Application...")
    print("[INFO] Current Stage: Step 22 (Final University Submission Preparation)")
    log.info("Starting SasthoSetu Desktop Application (Step 22)...")

    # 2. Initialize SQLite Database Schema
    try:
        from database import db

        db.initialize_database()
        print("[OK] SQLite database initialized successfully (sasthosetu.db).")
    except Exception as db_err:
        log.critical(f"Failed to initialize SQLite database: {db_err}")
        print(f"\n[FATAL ERROR] Failed to initialize SQLite database: {db_err}")
        sys.exit(1)

    # 3. Launch GUI Application
    try:
        import customtkinter as ctk
        from core import theme
        from ui.app import SasthoSetuApp

        # Apply application-wide visual theme
        ctk.set_appearance_mode(theme.APPEARANCE_MODE)
        ctk.set_default_color_theme(theme.DEFAULT_COLOR_THEME)

        print("[OK] CustomTkinter theme configured successfully.")
        print("[INFO] Launching main desktop window (1000x650)...")

        # Create and launch the application window
        app = SasthoSetuApp()

        def handle_tk_exception(exc_type, exc_val, exc_tb):
            err_msg = "".join(traceback.format_exception(exc_type, exc_val, exc_tb))
            log.error(f"Uncaught GUI Exception:\n{err_msg}")

        app.report_callback_exception = handle_tk_exception

        app.mainloop()

        log.info("Application window closed cleanly.")
        print("[INFO] Application window closed.")

    except ImportError as err:
        log.critical(f"Missing required dependency: {err}")
        print(f"\n[ERROR] Missing required dependency: {err}")
        print("[ACTION] Please run: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as fatal_err:
        log.critical(f"Fatal application error: {fatal_err}")
        print(f"\n[FATAL ERROR] {fatal_err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
