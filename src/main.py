"""
Speed Limit Recognition System
"""

import sys
import argparse
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


def main():
    parser = argparse.ArgumentParser(description='Speed Limit Recognition System')
    parser.add_argument('--gui', action='store_true', help='Launch GUI mode')
    args = parser.parse_args()

    if args.gui:
        run_gui()
    else:
        print("Use --gui to launch detection interface")


if __name__ == "__main__":
    main()
