"""
Speed Limit Detection GUI
"""

import sys
import logging
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QApplication, QFileDialog, QScrollArea, QLabel, QTabWidget
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap, QImage, QKeySequence, QShortcut, QDragEnterEvent, QDropEvent
import cv2

from src.core.detector import SpeedSignDetector
from src.core.video_processor import VideoProcessor
from src.gui.components import ControlBar, InfoBar, StatusBar, VideoControls
from src.gui.styles import AppStyles

logger = logging.getLogger(__name__)


class VideoProcessingThread(QThread):

    progress = Signal(int)
    finished = Signal(bool, str)

    def __init__(self, processor, input_path, output_path):
        super().__init__()
        self.processor = processor
        self.input_path = input_path
        self.output_path = output_path

    def run(self):
        try:
            success = self.processor.process_video(
                self.input_path,
                self.output_path,
                progress_callback=self.progress.emit
            )
            self.finished.emit(success, self.output_path)
        except Exception as e:
            logger.error(f"Video processing thread error: {e}")
            self.finished.emit(False, str(e))


class ImageViewer(QLabel):

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(1000, 700)
        self.setStyleSheet(AppStyles.IMAGE_LABEL)
        self.setAcceptDrops(True)
        self.drop_callback = None

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls and self.drop_callback:
            file_path = urls[0].toLocalFile()
            self.drop_callback(file_path)


class SimpleDetectionApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.detector = None
        self.video_processor = None
        self.image_files = []
        self.current_index = 0
        self.current_image = None
        self.cache = {}
        self.current_video_path = None
        self.video_thread = None

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

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(AppStyles.TAB_WIDGET)

        self.image_tab = self._create_image_tab()
        self.video_tab = self._create_video_tab()

        self.tabs.addTab(self.image_tab, "Image Detection")
        self.tabs.addTab(self.video_tab, "Video Processing")

        layout.addWidget(self.tabs)

        self.status_bar = StatusBar()
        layout.addWidget(self.status_bar)

    def _create_image_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

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

        return tab

    def _create_video_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        self.video_controls = VideoControls()
        self.video_controls.load_video.connect(self._load_video)
        self.video_controls.process_video.connect(self._process_video)
        layout.addWidget(self.video_controls)

        self.video_info_label = QLabel("No video loaded")
        self.video_info_label.setAlignment(Qt.AlignCenter)
        self.video_info_label.setStyleSheet(AppStyles.INFO_LABEL)
        layout.addWidget(self.video_info_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setAlignment(Qt.AlignCenter)
        scroll.setStyleSheet(AppStyles.SCROLL_AREA)

        self.video_preview = ImageViewer()
        self.video_preview.drop_callback = self._handle_video_drop
        scroll.setWidget(self.video_preview)
        layout.addWidget(scroll, 1)

        help_text = QLabel("Drag & Drop video file here or use 'Load Video' button\n"
                          "Supported formats: MP4, AVI, MOV, MKV")
        help_text.setAlignment(Qt.AlignCenter)
        help_text.setStyleSheet("color: #666; font-size: 12px; padding: 10px;")
        layout.addWidget(help_text)

        return tab

    def _setup_shortcuts(self):
        QShortcut(QKeySequence("Left"), self, self._previous_image)
        QShortcut(QKeySequence("Right"), self, self._next_image)
        QShortcut(QKeySequence("A"), self, self._previous_image)
        QShortcut(QKeySequence("D"), self, self._next_image)
        QShortcut(QKeySequence("Space"), self, self._detect_current)

    def _init_detector(self):
        try:
            self.detector = SpeedSignDetector()
            self.video_processor = VideoProcessor(self.detector)

            if self.detector.is_model_loaded():
                self.status_bar.set_status("Model loaded successfully")
            else:
                self.status_bar.set_status("Model not found, train first", "error")
        except Exception as e:
            logger.error(f"Detector init failed: {e}")
            self.status_bar.set_status(f"Error: {e}", "error")

    def _load_test_images(self):
        test_folder = Path("datasets/test_images")
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
                self._display_image(result_image, self.image_label)
                self._update_status(detections, cached=True)
            else:
                self._display_image(self.current_image, self.image_label)
                self.status_bar.set_status("Press Space to detect")

    def _display_image(self, cv_image, label_widget):
        rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)

        scaled = pixmap.scaled(
            label_widget.width(),
            label_widget.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        label_widget.setPixmap(scaled)

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
            self._display_image(result_image, self.image_label)
            self._update_status(detections, cached=True)
            return

        self.status_bar.set_status("Processing...")
        result_image, detections = self.detector.detect(self.current_image)

        self.cache[current_file] = (result_image, detections)
        self._display_image(result_image, self.image_label)
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

    def _load_video(self):
        video_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            str(Path("datasets/test_videos/input")),
            "Video Files (*.mp4 *.avi *.mov *.mkv);;All Files (*.*)"
        )

        if video_path:
            self._set_video(video_path)

    def _handle_video_drop(self, file_path):
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
        path = Path(file_path)

        if path.suffix.lower() in video_extensions:
            self._set_video(file_path)
        else:
            self.status_bar.set_status("Invalid video format", "error")

    def _set_video(self, video_path):
        self.current_video_path = video_path
        video_name = Path(video_path).name

        cap = cv2.VideoCapture(video_path)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                self._display_image(frame, self.video_preview)

            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps)

            self.video_info_label.setText(
                f"Video: {video_name}\n"
                f"Resolution: {width}x{height} | FPS: {fps} | Duration: {duration}s"
            )

            cap.release()
            self.video_controls.set_video_loaded(True)
            self.status_bar.set_status(f"Video loaded: {video_name}")
        else:
            self.status_bar.set_status("Cannot open video file", "error")

    def _process_video(self):
        if not self.current_video_path:
            return

        input_path = Path(self.current_video_path)
        output_dir = Path("datasets/test_videos/output")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = str(output_dir / f"{input_path.stem}_detected{input_path.suffix}")

        self.video_controls.set_processing(True)
        self.status_bar.set_status("Processing video...")

        self.video_thread = VideoProcessingThread(
            self.video_processor,
            self.current_video_path,
            output_path
        )

        self.video_thread.progress.connect(self._on_video_progress)
        self.video_thread.finished.connect(self._on_video_finished)
        self.video_thread.start()

    def _on_video_progress(self, progress):
        self.video_controls.update_progress(progress)
        self.status_bar.set_status(f"Processing video: {progress}%")

    def _on_video_finished(self, success, result):
        self.video_controls.set_processing(False)

        if success:
            self.status_bar.set_status(f"Video saved: {Path(result).name}")

            cap = cv2.VideoCapture(result)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    self._display_image(frame, self.video_preview)
                cap.release()
        else:
            self.status_bar.set_status(f"Processing failed: {result}", "error")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleDetectionApp()
    window.show()
    sys.exit(app.exec())
