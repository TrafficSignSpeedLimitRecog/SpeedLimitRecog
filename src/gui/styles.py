"""
GUI Styling and Theme Management
"""


class AppStyles:

    COLORS = {
        'primary': '#2196F3',
        'primary_dark': '#1976D2',
        'success': '#4CAF50',
        'success_dark': '#45a049',
        'warning': '#FF9800',
        'error': '#F44336',
        'error_light': '#ffebee',
        'error_dark': '#c62828',
        'light_bg': '#f5f5f5',
        'white': '#ffffff',
        'gray_light': '#fafafa',
        'gray_medium': '#cccccc',
        'gray_dark': '#666666',
        'border': '#ddd',
        'border_dashed': '#ccc',
        'info_bg': '#e3f2fd',
        'success_bg': '#e8f5e9',
        'success_text': '#2e7d32',
    }

    WINDOW = f"""
        QMainWindow {{
            background-color: {COLORS['light_bg']};
        }}
    """

    BUTTON = f"""
        QPushButton {{
            background-color: {COLORS['primary']};
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 13px;
            font-weight: bold;
            min-width: 120px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['primary_dark']};
        }}
        QPushButton:disabled {{
            background-color: {COLORS['gray_medium']};
            color: {COLORS['gray_dark']};
        }}
    """

    BUTTON_SUCCESS = f"""
        QPushButton {{
            background-color: {COLORS['success']};
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 13px;
            font-weight: bold;
            min-width: 120px;
        }}
        QPushButton:hover {{
            background-color: {COLORS['success_dark']};
        }}
        QPushButton:disabled {{
            background-color: {COLORS['gray_medium']};
            color: {COLORS['gray_dark']};
        }}
    """

    INFO_LABEL = f"""
        QLabel {{
            font-size: 14px;
            font-weight: bold;
            color: {COLORS['primary']};
            padding: 10px;
            background-color: {COLORS['info_bg']};
            border-radius: 5px;
        }}
    """

    SCROLL_AREA = f"""
        QScrollArea {{
            border: 2px solid {COLORS['border']};
            border-radius: 8px;
            background-color: {COLORS['white']};
        }}
    """

    IMAGE_LABEL = f"""
        QLabel {{
            background-color: {COLORS['gray_light']};
            border: 2px dashed {COLORS['border_dashed']};
            border-radius: 5px;
        }}
    """

    STATUS_SUCCESS = f"""
        QLabel {{
            font-size: 14px;
            padding: 12px;
            background-color: {COLORS['success_bg']};
            color: {COLORS['success_text']};
            border-radius: 5px;
            font-weight: bold;
        }}
    """

    STATUS_ERROR = f"""
        QLabel {{
            font-size: 14px;
            padding: 12px;
            background-color: {COLORS['error_light']};
            color: {COLORS['error_dark']};
            border-radius: 5px;
            font-weight: bold;
        }}
    """

    STATUS_WARNING = f"""
        QLabel {{
            font-size: 14px;
            padding: 12px;
            background-color: {COLORS['warning']};
            color: white;
            border-radius: 5px;
            font-weight: bold;
        }}
    """
