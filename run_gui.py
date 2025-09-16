import sys
from PySide6.QtWidgets import QApplication
from main_window import MainWindow
from theme import dark_theme  # <-- 1. IMPORT THE THEME

if __name__ == '__main__':
    # Create the application instance
    app = QApplication(sys.argv)

    # --- 2. APPLY THE THEME ---
    app.setStyleSheet(dark_theme)
    # --- END OF THEME APPLICATION ---

    # Create and show the main window
    window = MainWindow()
    window.show()

    # Start the application's event loop
    sys.exit(app.exec())