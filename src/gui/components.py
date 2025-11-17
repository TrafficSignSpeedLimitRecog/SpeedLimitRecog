"""
Reusable GUI Components
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QProgressBar, QSlider
from PySide6.QtCore import Signal, Qt
from .styles import AppStyles


class ControlBar(QWidget):

    load_folder = Signal()
    previous = Signal()
    next = Signal()
    detect = Signal()
    confidence_changed = Signal(float)

    def __init__(self):
        super().__init__()
        self.load_btn = None
        self.prev_btn = None
        self.next_btn = None
        self.detect_btn = None
        self.conf_slider = None
        self.conf_label = None
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

        # Confidence slider
        self.conf_label = QLabel("Confidence: 0.50")
        self.conf_label.setStyleSheet(f"color: {AppStyles.COLORS['text_primary']}; font-weight: bold; min-width: 120px;")

        self.conf_slider = QSlider(Qt.Horizontal)
        self.conf_slider.setRange(25, 95)
        self.conf_slider.setValue(50)
        self.conf_slider.setFixedWidth(150)
        self.conf_slider.setStyleSheet(AppStyles.SLIDER)
        self.conf_slider.valueChanged.connect(self._on_conf_changed)

        layout.addWidget(self.load_btn)
        layout.addStretch()
        layout.addWidget(self.conf_label)
        layout.addWidget(self.conf_slider)
        layout.addWidget(self.prev_btn)
        layout.addWidget(self.next_btn)
        layout.addWidget(self.detect_btn)

    def _on_conf_changed(self, value):
        conf = value / 100.0
        self.conf_label.setText(f"Confidence: {conf:.2f}")
        self.confidence_changed.emit(conf)

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


class VideoControls(QWidget):

    load_new_video = Signal()
    process_video = Signal()

    def __init__(self):
        super().__init__()
        self.load_video_btn = None
        self.process_btn = None
        self.progress_bar = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(10)

        self.load_video_btn = QPushButton("Load Video")
        self.load_video_btn.setStyleSheet(AppStyles.BUTTON)
        self.load_video_btn.clicked.connect(self.load_new_video.emit)
        self.load_video_btn.setEnabled(False)

        self.process_btn = QPushButton("Process Video")
        self.process_btn.setStyleSheet(AppStyles.BUTTON_SUCCESS)
        self.process_btn.clicked.connect(self.process_video.emit)
        self.process_btn.setEnabled(False)

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(AppStyles.PROGRESS_BAR)
        self.progress_bar.setVisible(False)

        layout.addWidget(self.load_video_btn)
        layout.addWidget(self.process_btn)
        layout.addWidget(self.progress_bar, 1)

    def set_video_loaded(self, loaded):
        self.process_btn.setEnabled(loaded)
        self.load_video_btn.setEnabled(loaded)

    def set_processing(self, processing):
        self.progress_bar.setVisible(processing)
        self.process_btn.setEnabled(not processing)
        self.load_video_btn.setEnabled(not processing)

    def update_progress(self, value):
        self.progress_bar.setValue(value)
