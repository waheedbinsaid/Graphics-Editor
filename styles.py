# styles.py

STYLESHEET = """
QWidget {
    background-color: #f8f9fa;
    color: #212529;
    font-family: "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}
QMenuBar {
    background-color: #ffffff;
    border-bottom: 1px solid #dee2e6;
}
QMenuBar::item:selected {
    background-color: #e9ecef;
}
QMenu {
    background-color: #ffffff;
    border: 1px solid #ced4da;
    padding: 5px;
}
QMenu::item {
    padding: 8px 20px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #4C6EF5;
    color: white;
}
QToolBar {
    background-color: #ffffff;
    border: none;
    padding: 8px;
    spacing: 8px;
}
QToolBar QToolButton {
    background-color: transparent;
    border-radius: 6px;
    padding: 10px;
    margin: 1px;
}
QToolBar QToolButton:hover {
    background-color: #e9ecef;
}
QToolBar QToolButton:checked {
    background-color: #dbe4ff;
}
QDockWidget::title {
    background-color: #ffffff;
    border-bottom: 1px solid #e9ecef;
    padding: 8px;
    font-weight: bold;
}
#inspectorPanel {
    background-color: #ffffff;
    border-radius: 0;
    font-size: 10pt;
}
#inspectorPanel QLabel {
    color: #495057;
    font-weight: 600;
}
#inspectorPanel QSpinBox, #inspectorPanel QComboBox {
    padding: 8px;
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 6px;
}
#inspectorPanel .color-button {
    border: 1px solid #dee2e6;
    border-radius: 6px;
    min-height: 28px;
}
#inspectorPanel .format-button {
    padding: 8px;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    font-weight: bold;
}
#inspectorPanel .format-button:checked {
    background-color: #dbe4ff;
    border-color: #4C6EF5;
}
QSlider::groove:horizontal {
    background: #e9ecef;
    height: 4px;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #4C6EF5;
    border: 4px solid white;
    width: 16px;
    height: 16px;
    margin: -7px 0;
    border-radius: 8px;
}
QGroupBox {
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    margin-top: 10px;
    padding: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    left: 10px;
}
#zoomPanel {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
}
#zoomPanel QPushButton, #zoomPanel QToolButton {
    font-weight: bold;
    border: none;
    background-color: transparent;
    padding: 5px 10px;
}
#zoomPanel QPushButton {
    font-size: 14pt;
}
#zoomPanel QToolButton {
    font-size: 10pt;
}
#zoomPanel QPushButton:hover, #zoomPanel QToolButton:hover {
    background-color: #f5f5f5;
}
QToolButton::menu-indicator {
    image: none;
}
"""
