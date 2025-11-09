"""
Reusable GUI Components
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal, Qt
from .styles import AppStyles


class ControlBar(QWidget):

    load_folder = Signal()
    previous = Signal()
    next = Signal()
    detect = Signal()

    def __init__(self):
        super().__init__()
        self.load_btn = None
        self.prev_btn = None
        self.next_btn = None
        self.detect_btn = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(10)

        self.load_btn = QPushButton("Load Folder")
        self.load_btn.setStyleSheet(AppStyles.BUTTON)
        self.load_btn.clicked.connect(self.load_folder.emit)

        self.prev_btn = QPushButton("<- Previous (A)")
        self.prev_btn.setStyleSheet(AppStyles.BUTTON)
        self.prev_btn.clicked.connect(self.previous.emit)
        self.prev_btn.setEnabled(False)

        self.next_btn = QPushButton("Next (D) ->")
        self.next_btn.setStyleSheet(AppStyles.BUTTON)
        self.next_btn.clicked.connect(self.next.emit)
        self.next_btn.setEnabled(False)

        self.detect_btn = QPushButton("Detect (Space)")
        self.detect_btn.setStyleSheet(AppStyles.BUTTON_SUCCESS)
        self.detect_btn.clicked.connect(self.detect.emit)

        layout.addWidget(self.load_btn)
        layout.addStretch()
        layout.addWidget(self.prev_btn)
        layout.addWidget(self.next_btn)
        layout.addWidget(self.detect_btn)

    def enable_navigation(self, enabled):
        self.prev_btn.setEnabled(enabled)
        self.next_btn.setEnabled(enabled)


class InfoBar(QLabel):

    def __init__(self):
        super().__init__("No images loaded")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(AppStyles.INFO_LABEL)

    def update_info(self, current, total, filename):
        if total > 0:
            self.setText(f"Image {current + 1} / {total}: {filename}")
        else:
            self.setText("No images loaded")


class StatusBar(QLabel):

    def __init__(self):
        super().__init__("Ready")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(AppStyles.STATUS_SUCCESS)

    def set_status(self, message, status_type="success"):
        self.setText(message)

        style_map = {
            "success": AppStyles.STATUS_SUCCESS,
            "error": AppStyles.STATUS_ERROR,
            "warning": AppStyles.STATUS_WARNING
        }

        self.setStyleSheet(style_map.get(status_type, AppStyles.STATUS_SUCCESS))
