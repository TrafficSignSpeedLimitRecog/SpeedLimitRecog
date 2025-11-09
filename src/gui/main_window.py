"""
Speed Limit Detection GUI
"""

import sys
import logging
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QApplication, QFileDialog, QScrollArea, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage, QKeySequence, QShortcut
import cv2

from src.core.detector import SpeedSignDetector
from src.gui.components import ControlBar, InfoBar, StatusBar
from src.gui.styles import AppStyles

logger = logging.getLogger(__name__)


class SimpleDetectionApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.detector = None
        self.image_files = []
        self.current_index = 0
        self.current_image = None
        self.cache = {}

        self._setup_ui()
        self._setup_shortcuts()
        self._init_detector()
        self._load_test_images()

    def _setup_ui(self):
        self.setWindowTitle("Speed Limit Detection System")
        self.setGeometry(100, 100, 1400, 900)
        self.setStyleSheet(AppStyles.WINDOW)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        self.control_bar = ControlBar()
        self.control_bar.load_folder.connect(self._load_folder)
        self.control_bar.previous.connect(self._previous_image)
        self.control_bar.next.connect(self._next_image)
        self.control_bar.detect.connect(self._detect_current)
        layout.addWidget(self.control_bar)

        self.info_bar = InfoBar()
        layout.addWidget(self.info_bar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setAlignment(Qt.AlignCenter)
        scroll.setStyleSheet(AppStyles.SCROLL_AREA)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(1000, 700)
        self.image_label.setStyleSheet(AppStyles.IMAGE_LABEL)
        scroll.setWidget(self.image_label)
        layout.addWidget(scroll, 1)

        self.status_bar = StatusBar()
        layout.addWidget(self.status_bar)

    def _setup_shortcuts(self):
        QShortcut(QKeySequence("Left"), self, self._previous_image)
        QShortcut(QKeySequence("Right"), self, self._next_image)
        QShortcut(QKeySequence("A"), self, self._previous_image)
        QShortcut(QKeySequence("D"), self, self._next_image)
        QShortcut(QKeySequence("Space"), self, self._detect_current)

    def _init_detector(self):
        try:
            self.detector = SpeedSignDetector()
            if self.detector.is_model_loaded():
                self.status_bar.set_status("Model loaded successfully")
            else:
                self.status_bar.set_status("Model not found, train first", "error")
        except Exception as e:
            logger.error(f"Detector init failed: {e}")
            self.status_bar.set_status(f"Error: {e}", "error")

    def _load_test_images(self):
        test_folder = Path("datasets/yolo_detection/test/images")
        if test_folder.exists():
            self._load_images_from_folder(test_folder)

    def _load_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Images Folder")
        if folder:
            self._load_images_from_folder(Path(folder))

    def _load_images_from_folder(self, folder_path):
        extensions = ['.jpg', '.jpeg', '.png', '.bmp']

        self.image_files = []
        for ext in extensions:
            self.image_files.extend(folder_path.glob(f'*{ext}'))
            self.image_files.extend(folder_path.glob(f'*{ext.upper()}'))

        seen = set()
        unique = []
        for f in self.image_files:
            if f.name.lower() not in seen:
                seen.add(f.name.lower())
                unique.append(f)

        self.image_files = [f for f in unique if f.name != '.gitkeep']
        self.image_files.sort()

        if self.image_files:
            self.current_index = 0
            self.cache = {}
            self.control_bar.enable_navigation(True)
            self._show_current_image()
            self.status_bar.set_status(f"Loaded {len(self.image_files)} images")
        else:
            self.status_bar.set_status("No images found", "warning")

    def _show_current_image(self):
        if not self.image_files:
            return

        current_file = self.image_files[self.current_index]
        self.info_bar.update_info(self.current_index, len(self.image_files), current_file.name)

        self.current_image = cv2.imread(str(current_file))

        if self.current_image is not None:
            if current_file in self.cache:
                result_image, detections = self.cache[current_file]
                self._display_image(result_image)
                self._update_status(detections, cached=True)
            else:
                self._display_image(self.current_image)
                self.status_bar.set_status("Press Space to detect")

    def _display_image(self, cv_image):
        rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)

        scaled = pixmap.scaled(
            self.image_label.width(),
            self.image_label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled)

    def _previous_image(self):
        if self.image_files and self.current_index > 0:
            self.current_index -= 1
            self._show_current_image()

    def _next_image(self):
        if self.image_files and self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self._show_current_image()

    def _detect_current(self):
        if self.current_image is None or self.detector is None:
            return

        current_file = self.image_files[self.current_index]

        if current_file in self.cache:
            result_image, detections = self.cache[current_file]
            self._display_image(result_image)
            self._update_status(detections, cached=True)
            return

        self.status_bar.set_status("Processing...")
        result_image, detections = self.detector.detect(self.current_image)

        self.cache[current_file] = (result_image, detections)
        self._display_image(result_image)
        self._update_status(detections)

    def _update_status(self, detections, cached=False):
        cache_text = " (cached)" if cached else ""

        if detections:
            speed_signs = [d for d in detections if d.get('speed_limit')]
            if speed_signs:
                speeds = [str(d['speed_limit']) for d in speed_signs]
                conf_avg = sum(d['confidence'] for d in speed_signs) / len(speed_signs)
                msg = f"Detected: {', '.join(speeds)} km/h (conf: {conf_avg:.2f}){cache_text}"
            else:
                msg = f"Other signs detected{cache_text}"
            self.status_bar.set_status(msg)
        else:
            self.status_bar.set_status(f"No signs detected{cache_text}", "warning")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleDetectionApp()
    window.show()
    sys.exit(app.exec())
