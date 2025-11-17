"""
GUI Styling and Theme Management - Dark Theme
"""


class AppStyles:

    COLORS = {
        'bg_dark': '#1e1e1e',
        'bg_darker': '#252526',
        'bg_lighter': '#2d2d30',
        'accent': '#007acc',
        'accent_hover': '#1e8ad6',
        'accent_dark': '#005a9e',
        'success': '#4ec9b0',
        'success_dark': '#3ea889',
        'warning': '#dcdcaa',
        'error': '#f48771',
        'error_dark': '#d16969',
        'text_primary': '#ffffff',
        'text_secondary': '#cccccc',
        'text_disabled': '#6e6e6e',
        'border': '#3e3e42',
        'border_light': '#555555',
        'tab_active': '#1e1e1e',
        'tab_inactive': '#2d2d30',
        'info_bg': '#264f78',
        'success_bg': '#1e3f34',
        'warning_bg': '#4d4d32',
        'error_bg': '#4b2020'
    }

    WINDOW = f"""
        QMainWindow {{
            background-color: {COLORS['bg_dark']};
        }}
    """

    BUTTON = f"""
        QPushButton {{
            background-color: {COLORS['accent']};
            color: {COLORS['text_primary']};
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            min-width: 120px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['accent_hover']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['accent_dark']};
        }}
        QPushButton:disabled {{
            background-color: {COLORS['bg_lighter']};
            color: {COLORS['text_disabled']};
        }}
    """

    BUTTON_SUCCESS = f"""
        QPushButton {{
            background-color: {COLORS['success']};
            color: {COLORS['bg_dark']};
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            min-width: 120px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['success_dark']};
        }}
        QPushButton:disabled {{
            background-color: {COLORS['bg_lighter']};
            color: {COLORS['text_disabled']};
        }}
    """

    INFO_LABEL = f"""
        QLabel {{
            font-size: 14px;
            font-weight: 600;
            color: {COLORS['text_primary']};
            padding: 12px 16px;
            background-color: {COLORS['info_bg']};
            border-radius: 6px;
            border-left: 4px solid {COLORS['accent']};
        }}
    """

    SCROLL_AREA = f"""
        QScrollArea {{
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            background-color: {COLORS['bg_darker']};
        }}
        QScrollBar:vertical {{
            background-color: {COLORS['bg_darker']};
            width: 12px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {COLORS['border_light']};
            border-radius: 6px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {COLORS['accent']};
        }}
    """

    IMAGE_LABEL = f"""
        QLabel {{
            background-color: {COLORS['bg_darker']};
            border: 2px dashed {COLORS['border']};
            border-radius: 8px;
            color: {COLORS['text_secondary']};
            font-size: 13px;
        }}
    """

    DROP_ZONE = f"""
        QLabel {{
            background-color: {COLORS['bg_darker']};
            border: 3px dashed {COLORS['accent']};
            border-radius: 12px;
            color: {COLORS['text_secondary']};
            font-size: 18px;
            font-weight: 600;
            padding: 40px;
        }}
        QLabel:hover {{
            background-color: {COLORS['bg_lighter']};
            border-color: {COLORS['accent_hover']};
            color: {COLORS['text_primary']};
        }}
    """

    STATUS_SUCCESS = f"""
        QLabel {{
            font-size: 13px;
            padding: 14px 18px;
            background-color: {COLORS['success_bg']};
            color: {COLORS['success']};
            border-radius: 6px;
            font-weight: 600;
            border-left: 4px solid {COLORS['success']};
        }}
    """

    STATUS_ERROR = f"""
        QLabel {{
            font-size: 13px;
            padding: 14px 18px;
            background-color: {COLORS['error_bg']};
            color: {COLORS['error']};
            border-radius: 6px;
            font-weight: 600;
            border-left: 4px solid {COLORS['error']};
        }}
    """

    STATUS_WARNING = f"""
        QLabel {{
            font-size: 13px;
            padding: 14px 18px;
            background-color: {COLORS['warning_bg']};
            color: {COLORS['warning']};
            border-radius: 6px;
            font-weight: 600;
            border-left: 4px solid {COLORS['warning']};
        }}
    """

    TAB_WIDGET = f"""
        QTabWidget::pane {{
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            background-color: {COLORS['bg_dark']};
            padding: 8px;
        }}
        QTabBar::tab {{
            background-color: {COLORS['tab_inactive']};
            color: {COLORS['text_secondary']};
            padding: 12px 28px;
            margin-right: 4px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            font-size: 13px;
            font-weight: 500;
        }}
        QTabBar::tab:selected {{
            background-color: {COLORS['accent']};
            color: {COLORS['text_primary']};
            font-weight: 700;
        }}
        QTabBar::tab:hover:!selected {{
            background-color: {COLORS['bg_lighter']};
            color: {COLORS['text_primary']};
        }}
    """

    PROGRESS_BAR = f"""
        QProgressBar {{
            border: 1px solid {COLORS['border']};
            border-radius: 6px;
            text-align: center;
            font-weight: 600;
            background-color: {COLORS['bg_darker']};
            color: {COLORS['text_primary']};
            height: 24px;
        }}
        QProgressBar::chunk {{
            background-color: {COLORS['success']};
            border-radius: 5px;
        }}
    """

    HELP_TEXT = f"""
        QLabel {{
            color: {COLORS['text_secondary']};
            font-size: 12px;
            padding: 12px;
            background-color: transparent;
        }}
    """

    PLAY_BUTTON = f"""
        QPushButton {{
            background-color: {COLORS['accent']};
            color: {COLORS['text_primary']};
            border: none;
            padding: 20px 60px;
            border-radius: 50px;
            font-size: 24px;
            font-weight: 700;
            min-width: 200px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['accent_hover']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['accent_dark']};
        }}
    """

    CONTROL_BUTTON = f"""
        QPushButton {{
            background-color: {COLORS['accent']};
            color: {COLORS['text_primary']};
            border: none;
            border-radius: 20px;
            font-size: 18px;
            font-weight: 700;
        }}
        QPushButton:hover {{
            background-color: {COLORS['accent_hover']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['accent_dark']};
        }}
    """

    SLIDER = f"""
        QSlider::groove:horizontal {{
            border: none;
            height: 6px;
            background-color: {COLORS['bg_lighter']};
            border-radius: 3px;
        }}
        QSlider::handle:horizontal {{
            background-color: {COLORS['accent']};
            width: 16px;
            height: 16px;
            margin: -5px 0;
            border-radius: 8px;
        }}
        QSlider::handle:horizontal:hover {{
            background-color: {COLORS['accent_hover']};
        }}
        QSlider::sub-page:horizontal {{
            background-color: {COLORS['accent']};
            border-radius: 3px;
        }}
    """
