"""
Application Entry Point

This is the main entry point for the Knowledge Base Management System.
It initializes the PyQt6 application and displays the main window.
"""

import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
