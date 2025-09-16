dark_theme = """
/* 
================================================================================
    HOI4 Save File Viewer - Dark Theme
================================================================================
*/

/* Global Styles */
QWidget {
    background-color: #2d2d2d; /* Dark grey background */
    color: #cccccc;            /* Light grey text */
    font-family: "Segoe UI", sans-serif;
    font-size: 10pt;
}

/* Main Window */
QMainWindow {
    background-color: #2d2d2d;
}

/* Labels */
QLabel {
    background-color: transparent;
}

/* Text Edit & Line Edit (Details Area & Search Bar) */
QTextEdit, QLineEdit {
    background-color: #222222; /* Slightly darker grey for inputs */
    color: #dddddd;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 5px;
}

QTextEdit {
    background-color: #1e1e1e; /* Parchment-like dark background */
}

/* Push Button */
QPushButton {
    background-color: #555555;
    color: #eeeeee;
    border: 1px solid #666666;
    border-radius: 4px;
    padding: 5px 10px;
}
QPushButton:hover {
    background-color: #666666;
    border: 1px solid #777777;
}
QPushButton:pressed {
    background-color: #4e6e58; /* HOI4 Green on press */
}

/* Tree View */
QTreeView {
    background-color: #222222;
    border: 1px solid #555555;
    alternate-background-color: #272727; /* Slightly different for alternating rows */
}
QTreeView::item {
    padding: 3px;
}
QTreeView::item:selected {
    background-color: #4e6e58; /* HOI4 Green for selection */
    color: #ffffff;
}
QTreeView::item:hover {
    background-color: #3a3a3a;
}

/* Tree View Header */
QHeaderView::section {
    background-color: #3d3d3d;
    color: #cccccc;
    padding: 4px;
    border: 1px solid #555555;
    font-weight: bold;
}

/* Splitter Handle */
QSplitter::handle {
    background-color: #3d3d3d;
}
QSplitter::handle:horizontal {
    width: 2px;
}
QSplitter::handle:vertical {
    height: 2px;
}

/* Scroll Bars */
QScrollBar:vertical {
    background: #222222;
    width: 12px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #444444;
    min-height: 20px;
    border-radius: 6px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background: #222222;
    height: 12px;
    margin: 0px;
}
QScrollBar::handle:horizontal {
    background: #444444;
    min-width: 20px;
    border-radius: 6px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Menu Bar */
QMenuBar {
    background-color: #3d3d3d;
}
QMenuBar::item {
    background: transparent;
    padding: 4px 8px;
}
QMenuBar::item:selected {
    background-color: #4e6e58; /* HOI4 Green */
}

/* Dropdown Menu */
QMenu {
    background-color: #3d3d3d;
    border: 1px solid #555555;
}
QMenu::item {
    padding: 4px 20px;
}
QMenu::item:selected {
    background-color: #4e6e58; /* HOI4 Green */
}
QMenu::separator {
    height: 1px;
    background: #555555;
    margin: 4px 0px;
}

/* Status Bar */
QStatusBar {
    background-color: #3d3d3d;
}

/* Message Box */
QMessageBox {
    background-color: #2d2d2d;
}
"""