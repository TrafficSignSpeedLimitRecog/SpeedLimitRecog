"""
Speed Limit Detection GUI
"""

import logging
import shutil
import sys
import cv2

from pathlib import Path

from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtGui import QIcon

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QMainWindow, QApplication, QFileDialog, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel, QSplitter
from PySide6.QtCore import Qt, QThread, Signal, QUrl
from PySide6.QtGui import QPixmap, QImage, QKeySequence, QShortcut, QDragEnterEvent, QDropEvent

from src.core.detector import SpeedSignDetector
from src.core.video_processor import VideoProcessor
from src.gui.components import InfoBar, StatusBar, VideoControls
from src.gui.log_widget import LogWidget
from src.gui.parameter_widget import ParameterWidget
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


class DropZoneLabel(QLabel):

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(AppStyles.DROP_ZONE)
        self.setAcceptDrops(True)
        self.drop_callback = None
        self.click_callback = None
        self.setText("Click or Drag & Drop Video\n\nSupported: MP4, AVI, MOV, MKV")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls and self.drop_callback:
            file_path = urls[0].toLocalFile()
            self.drop_callback(file_path)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.click_callback:
            self.click_callback()
        super().mousePressEvent(event)


class VideoPlayerWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.video_path = None
        self.is_playing = False
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        self.video_widget = QVideoWidget()
        self.video_widget.setStyleSheet("background-color: #000000;")
        self.player.setVideoOutput(self.video_widget)

        main_layout.addWidget(self.video_widget, 1)

        controls = QWidget()
        controls.setStyleSheet(AppStyles.VIDEO_CONTROLS)
        controls_layout = QHBoxLayout(controls)

        self.play_btn = QPushButton("Play")
        self.play_btn.setStyleSheet(AppStyles.BUTTON)
        self.play_btn.setFixedWidth(60)
        self.play_btn.clicked.connect(self._toggle_play)
        controls_layout.addWidget(self.play_btn)

        self.time_label = QLabel("00:00")
        self.time_label.setStyleSheet(f"color: {AppStyles.COLORS['text_primary']}; min-width: 50px;")
        controls_layout.addWidget(self.time_label)

        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setStyleSheet(AppStyles.SLIDER)
        self.position_slider.sliderMoved.connect(self._set_position)
        controls_layout.addWidget(self.position_slider, 1)

        self.duration_label = QLabel("00:00")
        self.duration_label.setStyleSheet(f"color: {AppStyles.COLORS['text_primary']}; min-width: 50px;")
        controls_layout.addWidget(self.duration_label)

        vol_label = QLabel("Vol")
        vol_label.setStyleSheet(f"color: {AppStyles.COLORS['text_primary']}; font-weight: bold;")
        controls_layout.addWidget(vol_label)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.setStyleSheet(AppStyles.SLIDER)
        self.volume_slider.valueChanged.connect(self._set_volume)
        controls_layout.addWidget(self.volume_slider)

        main_layout.addWidget(controls)

        self.player.positionChanged.connect(self._update_position)
        self.player.durationChanged.connect(self._update_duration)
        self.player.mediaStatusChanged.connect(self._handle_media_status)

        self._set_volume(50)

    def load_video(self, video_path):
        self.video_path = video_path
        self.player.setSource(QUrl.fromLocalFile(video_path))
        self.player.pause()

    def _toggle_play(self):
        if self.is_playing:
            self.player.pause()
            self.play_btn.setText("Play")
        else:
            self.player.play()
            self.play_btn.setText("Pause")
        self.is_playing = not self.is_playing

    def _set_position(self, position):
        self.player.setPosition(position)

    def _update_position(self, position):
        self.position_slider.setValue(position)
        self.time_label.setText(self._format_time(position))

    def _update_duration(self, duration):
        self.position_slider.setMaximum(duration)
        self.duration_label.setText(self._format_time(duration))

    def _set_volume(self, volume):
        self.audio_output.setVolume(volume / 100.0)

    @staticmethod
    def _format_time(ms):
        s = ms // 1000
        m, s = divmod(s, 60)
        return f"{m:02d}:{s:02d}"

    def _handle_media_status(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.player.setPosition(0)
            self.player.pause()
            self.is_playing = False
            self.play_btn.setText("Play")


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
        self.video_player = None
        self.log_widget = None
        self.parameter_widget = None

        self._setup_ui()
        self._setup_shortcuts()
        self._init_detector()
        self._load_test_images()

    def _setup_ui(self):
        self.setWindowTitle("Speed Limit Detection System")
        self.setGeometry(100, 50, 1800, 1000)
        self.setStyleSheet(AppStyles.WINDOW)

        icon_path = Path("assets/icon.png")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        self.parameter_widget = ParameterWidget()
        self.parameter_widget.parameters_changed.connect(self._on_parameters_changed)
        main_layout.addWidget(self.parameter_widget)

        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.setHandleWidth(2)
        content_splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {AppStyles.COLORS['border']};
            }}
        """)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(AppStyles.TAB_WIDGET)

        self.image_tab = self._create_image_tab()
        self.video_tab = self._create_video_tab()

        self.tabs.addTab(self.image_tab, "Image Detection")
        self.tabs.addTab(self.video_tab, "Video Processing")

        left_layout.addWidget(self.tabs)

        self.status_bar = StatusBar()
        left_layout.addWidget(self.status_bar)

        self.log_widget = LogWidget(max_lines=1000)
        self.log_widget.setMinimumWidth(400)
        self.log_widget.setMaximumWidth(600)

        content_splitter.addWidget(left_widget)
        content_splitter.addWidget(self.log_widget)
        content_splitter.setStretchFactor(0, 3)
        content_splitter.setStretchFactor(1, 1)

        main_layout.addWidget(content_splitter, 1)

        self.log_widget.add_log("Application started", "INFO")

    def _create_image_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)

        load_btn = QPushButton("Load Folder")
        load_btn.setStyleSheet(AppStyles.BUTTON)
        load_btn.clicked.connect(self._load_folder)
        controls_layout.addWidget(load_btn)

        controls_layout.addStretch()

        prev_btn = QPushButton("<- Previous (A)")
        prev_btn.setStyleSheet(AppStyles.BUTTON)
        prev_btn.clicked.connect(self._previous_image)
        prev_btn.setEnabled(False)
        self.prev_btn = prev_btn
        controls_layout.addWidget(prev_btn)

        next_btn = QPushButton("Next (D) ->")
        next_btn.setStyleSheet(AppStyles.BUTTON)
        next_btn.clicked.connect(self._next_image)
        next_btn.setEnabled(False)
        self.next_btn = next_btn
        controls_layout.addWidget(next_btn)

        detect_btn = QPushButton("Detect (Space)")
        detect_btn.setStyleSheet(AppStyles.BUTTON_SUCCESS)
        detect_btn.clicked.connect(self._detect_current)
        controls_layout.addWidget(detect_btn)

        layout.addLayout(controls_layout)

        self.info_bar = InfoBar()
        layout.addWidget(self.info_bar)

        self.image_container = QWidget()
        self.image_container.setStyleSheet(AppStyles.SCROLL_AREA)
        image_layout = QVBoxLayout(self.image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_layout.setAlignment(Qt.AlignCenter)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet(AppStyles.IMAGE_LABEL)
        self.image_label.setScaledContents(False)
        image_layout.addWidget(self.image_label)

        layout.addWidget(self.image_container, 1)

        return tab

    def _create_video_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)

        self.video_controls = VideoControls()
        self.video_controls.load_new_video.connect(self._load_video_on_click)
        self.video_controls.process_video.connect(self._process_video)
        layout.addWidget(self.video_controls)

        self.video_info_label = QLabel("No video loaded")
        self.video_info_label.setAlignment(Qt.AlignCenter)
        self.video_info_label.setStyleSheet(AppStyles.INFO_LABEL)
        layout.addWidget(self.video_info_label)

        self.video_container = QWidget()
        self.video_layout = QVBoxLayout(self.video_container)
        self.video_layout.setContentsMargins(0, 0, 0, 0)

        self.drop_zone = DropZoneLabel()
        self.drop_zone.drop_callback = self._handle_video_drop
        self.drop_zone.click_callback = self._load_video_on_click
        self.video_layout.addWidget(self.drop_zone)

        layout.addWidget(self.video_container, 1)

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
            self.video_processor.set_log_callback(self.log_widget.add_log)

            if self.detector.is_model_loaded():
                self.status_bar.set_status("Model loaded successfully")
                self.log_widget.add_log("Model loaded successfully", "SUCCESS")
            else:
                self.status_bar.set_status("Model not found, train first", "error")
                self.log_widget.add_log("Model not found", "ERROR")
        except Exception as e:
            logger.error(f"Detector init failed: {e}")
            self.status_bar.set_status(f"Error: {e}", "error")
            self.log_widget.add_log(f"Detector init failed: {e}", "ERROR")

    def _on_parameters_changed(self, params):
        if self.detector:
            conf = params.get('confidence_threshold')
            iou = params.get('iou_threshold')

            self.detector.update_parameters(conf=conf, iou=iou)
            self.cache = {}

            self.status_bar.set_status(f"Parameters updated: Conf={conf:.2f}, IoU={iou:.2f}")
            self.log_widget.add_log(f"Parameters updated: Conf={conf:.2f}, IoU={iou:.2f}", "INFO")

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
            self.prev_btn.setEnabled(True)
            self.next_btn.setEnabled(True)
            self._show_current_image()
            self.status_bar.set_status(f"Loaded {len(self.image_files)} images")
            self.log_widget.add_log(f"Loaded {len(self.image_files)} images from {folder_path.name}", "SUCCESS")
        else:
            self.status_bar.set_status("No images found", "warning")
            self.log_widget.add_log("No images found in folder", "WARNING")

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

    @staticmethod
    def _display_image(cv_image, label_widget):
        rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)

        container_width = label_widget.parent().width() - 40
        container_height = label_widget.parent().height() - 40

        scaled = pixmap.scaled(
            container_width,
            container_height,
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
            self.log_widget.add_log(f"Loaded cached detection for {current_file.name}", "INFO")
            return

        self.status_bar.set_status("Processing...")
        self.log_widget.add_log(f"Processing {current_file.name}", "INFO")

        result_image, detections = self.detector.detect(self.current_image)

        self.cache[current_file] = (result_image, detections)
        self._display_image(result_image, self.image_label)
        self._update_status(detections)

        if detections:
            det_str = ', '.join([f"{d['speed_limit']} km/h ({d['confidence']:.2f})" for d in detections if d.get('speed_limit')])
            self.log_widget.add_log(f"Detected: {det_str}", "SUCCESS")
        else:
            self.log_widget.add_log("No signs detected", "WARNING")

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

    def _load_video_on_click(self):
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
            self.log_widget.add_log(f"Invalid video format: {path.suffix}", "ERROR")

    def _set_video(self, video_path):
        input_dir = Path("datasets/test_videos/input")
        input_dir.mkdir(parents=True, exist_ok=True)

        video_file = Path(video_path)
        dest_path = input_dir / video_file.name

        if not dest_path.exists():
            shutil.copy2(video_path, dest_path)
            logger.info(f"Video copied to: {dest_path}")

        self.current_video_path = str(dest_path)
        video_name = video_file.name

        cap = cv2.VideoCapture(self.current_video_path)
        if cap.isOpened():
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps)

            self.video_info_label.setText(
                f"Video: {video_name}\n"
                f"Resolution: {width}x{height} | FPS: {fps} | Duration: {duration}s"
            )

            cap.release()

            self.drop_zone.hide()

            if self.video_player:
                self.video_layout.removeWidget(self.video_player)
                self.video_player.deleteLater()

            self.video_player = VideoPlayerWidget()
            self.video_player.load_video(self.current_video_path)
            self.video_layout.addWidget(self.video_player)

            self.video_controls.set_video_loaded(True)
            self.status_bar.set_status(f"Video loaded: {video_name}")
            self.log_widget.add_log(f"Video loaded: {video_name} ({width}x{height}, {fps}fps)", "SUCCESS")
        else:
            self.status_bar.set_status("Cannot open video file", "error")
            self.log_widget.add_log(f"Cannot open video file: {video_name}", "ERROR")

    def _process_video(self):
        if not self.current_video_path:
            return

        input_path = Path(self.current_video_path)
        output_dir = Path("datasets/test_videos/output")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = str(output_dir / f"{input_path.stem}_detected{input_path.suffix}")

        self.video_controls.set_processing(True)
        self.status_bar.set_status("Processing video...")
        self.log_widget.add_log(f"Started processing video: {input_path.name}", "INFO")

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
            self.log_widget.add_log(f"Video processing completed: {Path(result).name}", "SUCCESS")

            if self.video_player:
                self.video_player.load_video(result)

        else:
            self.status_bar.set_status(f"Processing failed: {result}", "error")
            self.log_widget.add_log(f"Video processing failed: {result}", "ERROR")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleDetectionApp()
    window.show()
    sys.exit(app.exec())
