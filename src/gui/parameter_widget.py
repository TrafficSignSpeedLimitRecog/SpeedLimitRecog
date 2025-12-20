from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel, QSlider, QPushButton
from PySide6.QtCore import Signal, Qt
from .styles import AppStyles


class ParameterWidget(QWidget):
    parameters_changed = Signal(dict)

    def __init__(self):
        super().__init__()
        self.default_values = {
            'confidence_threshold': 0.50,
            'iou_threshold': 0.45,
            'frame_skip': 1,
            'batch_size': 8
        }
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        detection_group = QGroupBox("Detection Parameters")
        detection_group.setStyleSheet(AppStyles.GROUP_BOX)
        detection_layout = QGridLayout(detection_group)
        detection_layout.setSpacing(12)
        detection_layout.setContentsMargins(15, 20, 15, 15)

        label_style = f"color: {AppStyles.COLORS['text_primary']}; font-size: 12px; font-weight: 600;"
        value_style = f"color: {AppStyles.COLORS['accent']}; font-size: 12px; font-weight: bold; min-width: 50px;"

        conf_label = QLabel("Confidence Threshold:")
        conf_label.setStyleSheet(label_style)
        detection_layout.addWidget(conf_label, 0, 0)

        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setRange(10, 95)
        self.confidence_slider.setValue(50)
        self.confidence_slider.setStyleSheet(AppStyles.SLIDER)
        self.confidence_slider.valueChanged.connect(self._on_parameters_changed)
        detection_layout.addWidget(self.confidence_slider, 0, 1)

        self.confidence_value = QLabel("0.50")
        self.confidence_value.setStyleSheet(value_style)
        self.confidence_value.setAlignment(Qt.AlignCenter)
        detection_layout.addWidget(self.confidence_value, 0, 2)

        iou_label = QLabel("IoU Threshold:")
        iou_label.setStyleSheet(label_style)
        detection_layout.addWidget(iou_label, 1, 0)

        self.iou_slider = QSlider(Qt.Horizontal)
        self.iou_slider.setRange(10, 90)
        self.iou_slider.setValue(45)
        self.iou_slider.setStyleSheet(AppStyles.SLIDER)
        self.iou_slider.valueChanged.connect(self._on_parameters_changed)
        detection_layout.addWidget(self.iou_slider, 1, 1)

        self.iou_value = QLabel("0.45")
        self.iou_value.setStyleSheet(value_style)
        self.iou_value.setAlignment(Qt.AlignCenter)
        detection_layout.addWidget(self.iou_value, 1, 2)

        skip_label = QLabel("Frame Skip (Video):")
        skip_label.setStyleSheet(label_style)
        detection_layout.addWidget(skip_label, 2, 0)

        self.skip_slider = QSlider(Qt.Horizontal)
        self.skip_slider.setRange(1, 5)
        self.skip_slider.setValue(1)
        self.skip_slider.setStyleSheet(AppStyles.SLIDER)
        self.skip_slider.valueChanged.connect(self._on_parameters_changed)
        detection_layout.addWidget(self.skip_slider, 2, 1)

        batch_label = QLabel("Batch Size (GPU):")
        batch_label.setStyleSheet(label_style)
        detection_layout.addWidget(batch_label, 3, 0)

        self.batch_slider = QSlider(Qt.Horizontal)
        self.batch_slider.setRange(1, 16)
        self.batch_slider.setValue(8)
        self.batch_slider.setStyleSheet(AppStyles.SLIDER)
        self.batch_slider.valueChanged.connect(self._on_parameters_changed)
        detection_layout.addWidget(self.batch_slider, 3, 1)

        self.batch_value = QLabel("8")
        self.batch_value.setStyleSheet(value_style)
        self.batch_value.setAlignment(Qt.AlignCenter)
        detection_layout.addWidget(self.batch_value, 3, 2)

        self.skip_value = QLabel("1")
        self.skip_value.setStyleSheet(value_style)
        self.skip_value.setAlignment(Qt.AlignCenter)
        detection_layout.addWidget(self.skip_value, 2, 2)

        layout.addWidget(detection_group)

        skip_info = QLabel("Frame skip: 1=best quality | Batch: 8=optimal for Heavy ex. (RTX 4090)")
        skip_info.setStyleSheet(f"color: {AppStyles.COLORS['text_secondary']}; font-size: 10px; margin-left: 10px;")
        layout.addWidget(skip_info)

        reset_layout = QHBoxLayout()
        reset_layout.addStretch()

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setStyleSheet(AppStyles.BUTTON)
        reset_btn.setMaximumWidth(150)
        reset_btn.clicked.connect(self._reset_defaults)
        reset_layout.addWidget(reset_btn)

        layout.addLayout(reset_layout)
        layout.addStretch()

    def _on_parameters_changed(self):
        conf = self.confidence_slider.value() / 100.0
        iou = self.iou_slider.value() / 100.0
        skip = self.skip_slider.value()
        batch = self.batch_slider.value()

        self.confidence_value.setText(f"{conf:.2f}")
        self.iou_value.setText(f"{iou:.2f}")
        self.skip_value.setText(f"{skip}")
        self.batch_value.setText(f"{batch}")

        params = {
            'confidence_threshold': conf,
            'iou_threshold': iou,
            'frame_skip': skip,
            'batch_size': batch
        }
        self.parameters_changed.emit(params)

    def _reset_defaults(self):
        self.confidence_slider.setValue(int(self.default_values['confidence_threshold'] * 100))
        self.iou_slider.setValue(int(self.default_values['iou_threshold'] * 100))
        self.skip_slider.setValue(self.default_values['frame_skip'])
        self.batch_slider.setValue(self.default_values['batch_size'])

    def get_parameters(self):
        return {
            'confidence_threshold': self.confidence_slider.value() / 100.0,
            'iou_threshold': self.iou_slider.value() / 100.0,
            'frame_skip': self.skip_slider.value(),
            'batch_size': self.batch_slider.value()
        }
