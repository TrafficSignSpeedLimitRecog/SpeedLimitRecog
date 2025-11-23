import time
from pathlib import Path

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QCheckBox, QLabel, QFileDialog, \
    QMessageBox

from .styles import AppStyles


class LogWidget(QWidget):

    def __init__(self, max_lines=1000):
        super().__init__()
        self.max_lines = max_lines
        self.log_lines = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)

        clear_btn = QPushButton("Clear")
        clear_btn.setMaximumWidth(80)
        clear_btn.setStyleSheet(AppStyles.BUTTON)
        clear_btn.clicked.connect(self.clear_logs)
        controls_layout.addWidget(clear_btn)

        export_btn = QPushButton("Export")
        export_btn.setMaximumWidth(80)
        export_btn.setStyleSheet(AppStyles.BUTTON)
        export_btn.clicked.connect(self.export_logs)
        controls_layout.addWidget(export_btn)

        self.auto_scroll_check = QCheckBox("Auto-scroll")
        self.auto_scroll_check.setChecked(True)
        self.auto_scroll_check.setStyleSheet(AppStyles.CHECKBOX)
        controls_layout.addWidget(self.auto_scroll_check)

        controls_layout.addStretch()

        self.info_label = QLabel("Ready")
        self.info_label.setStyleSheet(f"color: {AppStyles.COLORS['accent']}; font-size: 11px; font-weight: 600;")
        controls_layout.addWidget(self.info_label)

        layout.addLayout(controls_layout)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(AppStyles.LOG_TEXT_EDIT)
        self.log_text.document().setMaximumBlockCount(self.max_lines)
        layout.addWidget(self.log_text)

    def add_log(self, message, level="INFO"):
        timestamp = time.strftime("%H:%M:%S")

        color_map = {
            "ERROR": "#ff4444",
            "WARNING": "#ffaa00",
            "INFO": "#ffffff",
            "SUCCESS": "#4ec9b0"
        }

        color = color_map.get(level, "#ffffff")
        formatted_msg = f'<span style="color: {color}">[{timestamp}] [{level}] {message}</span>'

        self.log_text.append(formatted_msg)

        if self.auto_scroll_check.isChecked():
            scrollbar = self.log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

        plain_log = f"[{timestamp}] [{level}] {message}"
        self.log_lines.append(plain_log)

        self.info_label.setText(f"{len(self.log_lines)} log entries")

    def clear_logs(self):
        self.log_text.clear()
        self.log_lines.clear()
        self.info_label.setText("Logs cleared")

    def export_logs(self):
        if not self.log_lines:
            QMessageBox.information(self, "Export Logs", "No logs to export.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Logs",
            str(Path.home() / "speed_limit_logs.txt"),
            "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(self.log_lines))

                self.add_log(f"Logs exported to {Path(file_path).name}", "SUCCESS")
                QMessageBox.information(self, "Export Complete", "Logs exported successfully!")
            except Exception as e:
                self.add_log(f"Export failed: {e}", "ERROR")
                QMessageBox.critical(self, "Export Failed", f"Failed to export logs: {str(e)}")
