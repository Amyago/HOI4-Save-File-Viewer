import traceback
from PySide6.QtCore import QObject, Signal, Slot
from hoi4.parse import load_as_text, filestring_to_dict


class Worker(QObject):
    """
    A worker object that runs in a separate thread to handle long-running tasks
    like file parsing, ensuring the GUI remains responsive.
    """
    # Signal now emits a tuple: (dictionary, plain_text)
    result_ready = Signal(tuple)

    # Signal emitted to update the status bar with progress messages
    progress = Signal(str)

    # Signal emitted when an error occurs during the task
    error = Signal(str)

    def __init__(self):
        super().__init__()
        self._file_path = ""

    @Slot(str)
    def set_task(self, file_path):
        """Sets the file path for the parsing task."""
        self._file_path = file_path

    @Slot()
    def run(self):
        """
        Executes the parsing task. It first gets the plain text, then creates
        the dictionary from it, and finally emits both as a tuple.
        """
        try:
            self.progress.emit(f"Parsing {self._file_path}...")

            # Step 1: Get the plain text representation. This handles both
            # binary and plain-text .hoi4 files.
            plain_text = load_as_text(self._file_path)

            # Step 2: Create the dictionary from the plain text.
            # This is much faster than parsing the file a second time.
            data_dict = filestring_to_dict(plain_text)

            # Step 3: Emit both results together in a tuple.
            self.result_ready.emit((data_dict, plain_text))

            self.progress.emit("Parsing complete.")

        except Exception as e:
            # If any error occurs, emit the error signal with a detailed message
            error_message = f"Error parsing file: {e}\n{traceback.format_exc()}"
            self.error.emit(error_message)