"""
Video Player with Scaling
"""

from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import QWidget, QVBoxLayout

class VideoPlayer(QWidget):

    def __init__(self):
        super().__init__()
        self.video_path = None
        self.is_playing = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        self.video_widget = QVideoWidget()
        self.player.setVideoOutput(self.video_widget)

        layout.addWidget(self.video_widget)

    def load_video(self, video_path):
        from PySide6.QtCore import QUrl
        self.video_path = video_path
        self.player.setSource(QUrl.fromLocalFile(video_path))

    def play(self):
        self.player.play()
        self.is_playing = True

    def pause(self):
        self.player.pause()
        self.is_playing = False

    def stop(self):
        self.player.stop()
        self.is_playing = False
