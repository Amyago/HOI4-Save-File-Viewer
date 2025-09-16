# In tree_model.py

from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt
from PySide6.QtGui import QColor

from diff_logic import DiffNode, DiffStatus


class TreeItem:
    """A helper class to represent a node in the single-file tree model."""

    def __init__(self, key, value, parent=None):
        self._parent = parent
        self._key = key
        self._value = value
        self._children = []

    def appendChild(self, item):
        self._children.append(item)

    def child(self, row):
        if 0 <= row < len(self._children):
            return self._children[row]
        return None

    def childCount(self):
        return len(self._children)

    def parentItem(self):
        return self._parent

    def row(self):
        if self._parent:
            return self._parent._children.index(self)
        return 0

    def get_path(self):
        path = []
        current = self
        while current and current.parentItem() and current.parentItem()._key != "__root__":
            path.insert(0, str(current._key))
            current = current.parentItem()
        return " -> ".join(path)


class TreeModel(QAbstractItemModel):
    """
    A model for displaying data in a QTreeView. It now treats TreeItem and DiffNode
    polymorphically thanks to their standardized interface.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rootItem = TreeItem("__root__", {})
        self.is_diff_mode = False

    def setup_single_file_data(self, data):
        self.beginResetModel()
        self.is_diff_mode = False
        self._rootItem = TreeItem("__root__", data)
        self._populate_tree(data, self._rootItem)
        self.endResetModel()

    def setup_diff_data(self, diff_root_node):
        self.beginResetModel()
        self.is_diff_mode = True
        self._rootItem = diff_root_node
        self.endResetModel()

    def _populate_tree(self, data, parent):
        if isinstance(data, dict):
            for key, value in data.items():
                child_item = TreeItem(str(key), value, parent)
                parent.appendChild(child_item)
                if isinstance(value, (dict, list)):
                    self._populate_tree(value, child_item)
        elif isinstance(data, list):
            for i, value in enumerate(data):
                child_item = TreeItem(f"[{i}]", value, parent)
                parent.appendChild(child_item)
                if isinstance(value, (dict, list)):
                    self._populate_tree(value, child_item)

    def columnCount(self, parent=QModelIndex()):
        return 3 if self.is_diff_mode else 2

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid(): return None
        item = index.internalPointer()

        if role == Qt.DisplayRole:
            if isinstance(item, TreeItem):
                if index.column() == 0: return item._key
                if index.column() == 1:
                    if isinstance(item._value, (dict, list)): return f"[{len(item._value)} items]"
                    return str(item._value)
            elif isinstance(item, DiffNode):
                if index.column() == 0: return item.key
                if index.column() == 1: return str(item.value_b)
                if index.column() == 2: return str(item.value_a)

        if role == Qt.BackgroundRole and self.is_diff_mode and isinstance(item, DiffNode):
            if item.status == DiffStatus.ADDED: return QColor("#1a421a")
            if item.status == DiffStatus.REMOVED: return QColor("#4d1f1f")
            if item.status == DiffStatus.MODIFIED: return QColor("#544319")

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == 0: return "Key"
            if self.is_diff_mode:
                if section == 1: return "New Value (File 2)"
                if section == 2: return "Old Value (File 1)"
            else:
                if section == 1: return "Value"
        return None

    # --- SIMPLIFIED AND CORRECTED METHODS ---
    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent): return QModelIndex()
        parentItem = parent.internalPointer() if parent.isValid() else self._rootItem
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        return QModelIndex()

    def parent(self, index):
        if not index.isValid(): return QModelIndex()
        childItem = index.internalPointer()
        parentItem = childItem.parentItem()
        if parentItem == self._rootItem:
            return QModelIndex()
        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=QModelIndex()):
        if parent.column() > 0: return 0
        parentItem = parent.internalPointer() if parent.isValid() else self._rootItem
        return parentItem.childCount()
    # --- END OF SIMPLIFIED METHODS ---