import json
from PySide6.QtCore import (QThread, Qt, QSortFilterProxyModel, QModelIndex, QRegularExpression, QSettings)
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QTreeView, QTextEdit, QLineEdit, QSplitter, QProgressDialog,
                               QStatusBar, QFileDialog, QMessageBox, QStackedWidget, QLabel, QPushButton)
from PySide6.QtGui import QAction, QKeySequence, QFont

from worker import Worker
from tree_model import TreeModel, TreeItem
from pathlib import Path
from hoi4.parse import load_as_dict # We need this for the comparison file
from diff_logic import compare_dicts, DiffNode

# (FilterProxyModel class remains the same as before)
class FilterProxyModel(QSortFilterProxyModel):
    """A proxy model for filtering the tree view based on search text."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRecursiveFilteringEnabled(True)

    def filterAcceptsRow(self, source_row, source_parent):
        if not self.filterRegularExpression().pattern():
            return True
        index0 = self.sourceModel().index(source_row, 0, source_parent)
        if not index0.isValid():
            return False
        key_data = str(self.sourceModel().data(index0, Qt.DisplayRole))
        if self.filterRegularExpression().match(key_data).hasMatch():
            return True
        index1 = self.sourceModel().index(source_row, 1, source_parent)
        value_data = str(self.sourceModel().data(index1, Qt.DisplayRole))
        if self.filterRegularExpression().match(value_data).hasMatch():
            return True
        if self.sourceModel().hasChildren(index0):
            for i in range(self.sourceModel().rowCount(index0)):
                if self.filterAcceptsRow(i, index0):
                    return True
        return False


class MainWindow(QMainWindow):
    """The main window of the HOI4 Save File Viewer application."""

    def __init__(self):
        super().__init__()
        self.settings = QSettings("HOI4ViewerCommunity", "HOI4SaveViewer")
        self.setWindowTitle("HOI4 Save File Viewer")
        self.setGeometry(100, 100, 1200, 800)

        # --- Data Storage ---
        self.current_file_path = None
        self.parsed_data_dict = None
        self.parsed_data_text = None  # New variable to store plain text

        # --- Worker Thread Setup ---
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)
        self.worker.result_ready.connect(self.on_parsing_finished)  # Connect to the updated slot
        self.worker.progress.connect(self.update_status_bar)
        self.worker.error.connect(self.on_parsing_error)
        self.thread.started.connect(self.worker.run)

        # --- UI Setup ---
        self._create_actions()
        self._create_menu_bar()
        self._create_main_widget()
        self.setStatusBar(QStatusBar(self))
        self.update_status_bar("Ready. Open a .hoi4 save file to begin.")
        self.stacked_widget.setCurrentIndex(0)  # Start on the Welcome Screen

        self.is_diff_mode = False  # Add this flag

    def _create_actions(self):
        """Create actions for the menu bar."""
        self.open_action = QAction("&Open Save File...", self)
        self.open_action.triggered.connect(self.open_file)
        self.open_action.setShortcut(QKeySequence.Open)

        self.open_default_action = QAction("Open &Default Save Folder...", self)
        # We connect it to the same open_file slot, but will use a lambda to pass a parameter
        self.open_default_action.triggered.connect(lambda: self.open_file(use_default_path=True))

        self.save_json_action = QAction("Save as &JSON...", self)
        self.save_json_action.triggered.connect(self.save_as_json)
        self.save_json_action.setEnabled(False)

        self.save_text_action = QAction("Save as Plain &Text...", self)
        self.save_text_action.triggered.connect(self.save_as_text)
        self.save_text_action.setEnabled(False)

        self.exit_action = QAction("E&xit", self)
        self.exit_action.triggered.connect(self.close)

        self.compare_action = QAction("&Compare With...", self)
        self.compare_action.triggered.connect(self.compare_file)
        self.compare_action.setEnabled(False)  # Disabled until a file is loaded

    def _create_menu_bar(self):
        """Create the application's menu bar."""
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.open_default_action)
        save_menu = file_menu.addMenu("Save Parsed Data As...")
        save_menu.addAction(self.save_json_action)
        save_menu.addAction(self.save_text_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.open_default_action)
        file_menu.addAction(self.compare_action)  # Add the compare action

    def _create_main_widget(self):
        """
        Creates the central widget, which is now a QStackedWidget to switch
        between the welcome screen and the data view.
        """
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create the two "pages" for the stack
        welcome_widget = self._create_welcome_widget()
        data_widget = self._create_data_widget()

        # Add them to the stack
        self.stacked_widget.addWidget(welcome_widget)
        self.stacked_widget.addWidget(data_widget)

    def _create_welcome_widget(self):
        """Creates the initial welcoming screen with a large 'Open File' button."""
        welcome_widget = QWidget()
        layout = QVBoxLayout(welcome_widget)
        layout.setAlignment(Qt.AlignCenter)  # Center everything

        # Main Title
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label = QLabel("HOI4 Save File Viewer")
        title_label.setFont(title_font)

        # Subtitle/Instruction
        subtitle_label = QLabel("Open a .hoi4 file to begin")
        subtitle_label.setAlignment(Qt.AlignCenter)

        # Large "Open File" Button
        open_button = QPushButton("Open a Save File...")
        open_button.setFixedSize(200, 50)  # Make the button a nice size
        open_button.clicked.connect(self.open_file)  # Connect to existing function

        layout.addStretch()  # Add space above
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addSpacing(20)
        layout.addWidget(open_button, alignment=Qt.AlignCenter)
        layout.addStretch()  # Add space below

        return welcome_widget

    def _create_data_widget(self):
        """Creates the main data view with the tree and details panel."""
        # This is the original logic from the old _create_main_widget method
        data_widget = QSplitter(Qt.Horizontal)

        # Left Panel: Tree View
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        self.tree_view = QTreeView()
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.header().setStretchLastSection(True)
        left_layout.addWidget(self.tree_view)

        # Right Panel: Search and Details
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search in tree...")
        self.search_bar.textChanged.connect(self.filter_tree)
        self.details_area = QTextEdit()
        self.details_area.setReadOnly(True)
        self.details_area.setFontFamily("Courier")

        right_layout.addWidget(self.search_bar)
        right_layout.addWidget(self.details_area)

        # --- ADD THIS LEGEND ---
        self.legend_label = QLabel(
            '<font color="#66bb6a">■ Added</font> &nbsp; '
            '<font color="#ef5350">■ Removed</font> &nbsp; '
            '<font color="#ffa726">■ Modified</font>'
        )
        self.legend_label.setVisible(False)  # Hide it initially
        right_layout.addWidget(self.legend_label)
        # --- END ADD ---

        data_widget.addWidget(left_panel)
        data_widget.addWidget(right_panel)
        data_widget.setSizes([400, 300])

        # Setup Tree Model (moved from old method)
        self.tree_model = TreeModel()
        self.proxy_model = FilterProxyModel(self)
        self.proxy_model.setSourceModel(self.tree_model)
        self.tree_view.setModel(self.proxy_model)
        self.tree_view.selectionModel().selectionChanged.connect(self.on_tree_selection_changed)

        return data_widget

    def _get_default_save_path(self):
        """Finds the default HOI4 save game path for the current OS."""
        # The standard path is Documents/Paradox Interactive/Hearts of Iron IV/save games
        save_game_path = Path.home() / "Documents" / "Paradox Interactive" / "Hearts of Iron IV" / "save games"

        if save_game_path.is_dir():
            return str(save_game_path)
        else:
            # If it's not found, fall back to the user's home directory
            return str(Path.home())

    def update_status_bar(self, message):
        """Updates the text in the status bar."""
        self.statusBar().showMessage(message)

    def open_file(self, use_default_path=False):
        """
        Opens a file dialog to select a .hoi4 save file and starts parsing.
        This method now handles both "Open..." and "Open Default...".
        """

        # --- ADD RESET LOGIC AT THE TOP ---
        if self.is_diff_mode:
            self.is_diff_mode = False
            self.legend_label.setVisible(False)
            self.tree_view.header().setStretchLastSection(True)  # Reset column stretch
        # --- END ADD ---

        if self.thread.isRunning():
            QMessageBox.warning(self, "Busy", "A file is already being parsed. Please wait.")
            return

        # --- SMART DIRECTORY LOGIC ---
        start_dir = ""
        if use_default_path:
            # If the user clicked "Open Default...", we use that specific path.
            start_dir = self._get_default_save_path()
        else:
            # Otherwise, we try to get the last used directory from settings.
            # If it's not there, we fall back to the default path as a convenience.
            start_dir = self.settings.value("last_dir", self._get_default_save_path())
        # --- END OF LOGIC ---

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open HOI4 Save File",
            dir=start_dir,  # <-- FIX: The keyword is 'dir', not 'directory'
            filter="HOI4 Save Files (*.hoi4)"
        )

        if file_path:
            self.stacked_widget.setCurrentIndex(1)  # Switch to the Data View
            # --- REMEMBER DIRECTORY LOGIC ---
            # Get the parent folder of the file they chose
            directory = str(Path(file_path).parent)
            # Save this path to our settings for next time
            self.settings.setValue("last_dir", directory)
            # --- END OF LOGIC ---

            self.current_file_path = file_path
            self.tree_model.setup_single_file_data({})
            self.details_area.clear()
            self.save_json_action.setEnabled(False)
            self.save_text_action.setEnabled(False)
            self.compare_action.setEnabled(False)  # Disable compare until parse is done
            self.worker.set_task(file_path)
            self.thread.start()

    def save_as_json(self):
        """Saves the parsed dictionary data as a JSON file."""
        if self.parsed_data_dict is None:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save as JSON", "", "JSON Files (*.json)")

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.parsed_data_dict, f, indent=4)
                self.update_status_bar(f"Successfully saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Could not save JSON file:\n{e}")

    def save_as_text(self):
        """Saves the plain text representation of the save file instantly."""
        # This function no longer needs to call any slow parsing functions.
        if self.parsed_data_text is None:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save as Plain Text", "", "Text Files (*.txt)")

        if file_path:
            try:
                # Simply write the stored plain text to the file.
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.parsed_data_text)
                self.update_status_bar(f"Successfully saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Could not save plain text file:\n{e}")

    def on_parsing_finished(self, results):
        """
        Handles the successful completion of the parsing task.
        Receives a tuple containing both the dictionary and the plain text.
        """
        self.thread.quit()
        self.thread.wait()

        # Unpack the results tuple
        self.parsed_data_dict, self.parsed_data_text = results

        # --- USE THE CORRECT SETUP METHOD ---
        self.tree_model.setup_single_file_data(self.parsed_data_dict)

        self.save_json_action.setEnabled(True)
        self.save_text_action.setEnabled(True)
        self.compare_action.setEnabled(True)  # Enable the compare button
        self.update_status_bar("Ready.")

        # --- AUTO-EXPAND LOGIC ---
        # Get the root index (which is an empty QModelIndex)
        parent_index = QModelIndex()
        # Get the number of top-level items from our proxy model
        num_top_level_items = self.proxy_model.rowCount(parent_index)

        # Loop through each top-level item and expand it
        for row in range(num_top_level_items):
            # Get the index of the child item in the first column
            child_index = self.proxy_model.index(row, 0, parent_index)
            # Tell the tree view to expand that item
            if child_index.isValid():
                self.tree_view.expand(child_index)
        # --- END OF AUTO-EXPAND LOGIC ---

    def on_parsing_error(self, message):
        # This function remains unchanged
        self.thread.quit()
        self.thread.wait()
        self.stacked_widget.setCurrentIndex(0)  # Switch back to Welcome Screen
        QMessageBox.critical(self, "Parsing Error", message)
        self.update_status_bar("Error: Failed to parse file.")

    def on_tree_selection_changed(self, selected, deselected):
        indexes = selected.indexes()
        if not indexes:
            return

        proxy_index = indexes[0]
        source_index = self.proxy_model.mapToSource(proxy_index)
        item = source_index.internalPointer()

        # --- CORRECTED LOGIC ---
        if self.is_diff_mode and isinstance(item, DiffNode):
            # Build the path by walking up the tree
            path_parts = []
            current = item
            while current and current.parentItem() and current.key != '__root__':
                path_parts.insert(0, str(current.key))
                current = current.parentItem()
            path = " -> ".join(path_parts)

            details_text = (
                f"Path: {path}\n"
                f"Key: {item.key}\n"
                f"Status: {item.status.name}\n"
                "--------------------\n"
                f"Old Value (File 1):\n{item.value_a}\n"
                "--------------------\n"
                f"New Value (File 2):\n{item.value_b}"
            )
            self.details_area.setText(details_text)
        elif not self.is_diff_mode and isinstance(item, TreeItem):
            # ... (original logic for single-file view) ...
            key = item._key
            value = item._value
            path = item.get_path()
            details_text = f"Path: {path}\n"
            details_text += f"Key: {key}\n"
            details_text += "--------------------\n"
            if isinstance(value, (dict, list)):
                try:
                    value_str = json.dumps(value, indent=4)
                except (TypeError, OverflowError):
                    value_str = str(value)
            else:
                value_str = str(value)
            details_text += f"Value:\n{value_str}"
            self.details_area.setText(details_text)

    def filter_tree(self, text):
        # This function remains unchanged
        search = QRegularExpression(text, QRegularExpression.CaseInsensitiveOption)
        self.proxy_model.setFilterRegularExpression(search)

    def closeEvent(self, event):
        # This function remains unchanged
        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        event.accept()

    def compare_file(self):
        if not self.current_file_path or not self.parsed_data_dict:
            QMessageBox.information(self, "No Base File", "Please open a base save file first before comparing.")
            return

        file_path_b, _ = QFileDialog.getOpenFileName(
            self, f"Compare '{Path(self.current_file_path).name}' With...",
            dir=self.settings.value("last_dir", self._get_default_save_path()),
            filter="HOI4 Save Files (*.hoi4)"
        )

        if not file_path_b:
            return

        # --- PARSE SECOND FILE WITH A PROGRESS DIALOG ---
        # This prevents the UI from freezing during the second parse
        progress = QProgressDialog("Parsing comparison file...", "Cancel", 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()

        try:
            dict_b = load_as_dict(file_path_b)
        except Exception as e:
            QMessageBox.critical(self, "Parsing Error", f"Could not parse the comparison file:\n{e}")
            progress.close()
            return

        progress.setLabelText("Comparing files...")

        # Now perform the diff
        diff_root = compare_dicts(self.parsed_data_dict, dict_b)
        self.on_comparison_finished(diff_root)
        progress.close()

    def on_comparison_finished(self, diff_root):
        """Called when the diff is ready to be displayed."""
        self.is_diff_mode = True
        self.tree_model.setup_diff_data(diff_root)

        # Update UI for diff mode
        self.tree_view.header().setVisible(True)  # Ensure header is visible
        self.tree_view.setColumnWidth(0, 250)
        self.tree_view.setColumnWidth(1, 150)
        self.tree_view.setColumnWidth(2, 150)
        self.legend_label.setVisible(True)
        self.details_area.clear()
        self.update_status_bar("Comparison complete. Green = Added, Red = Removed, Yellow = Modified.")
        self.tree_view.expandToDepth(0)