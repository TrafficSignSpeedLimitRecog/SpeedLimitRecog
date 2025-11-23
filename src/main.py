"""
Speed Limit Recognition System
"""

import sys
import logging
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from src.gui.main_window import SimpleDetectionApp

logging.basicConfig(level=logging.INFO)


def run_gui():
    app = QApplication(sys.argv)
    window = SimpleDetectionApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_gui()
