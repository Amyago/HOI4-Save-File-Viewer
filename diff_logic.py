# In diff_logic.py

from enum import Enum


# Define the possible states for a diff node
class DiffStatus(Enum):
    UNCHANGED = 0
    MODIFIED = 1
    ADDED = 2
    REMOVED = 3


class DiffNode:
    """
    Represents a node in the comparison tree.
    This class now has the same interface as TreeItem for compatibility with the model.
    """

    def __init__(self, key, value_a=None, value_b=None, status=DiffStatus.UNCHANGED, parent=None):
        self.key = key
        self.value_a = value_a  # Value from the first file (old)
        self.value_b = value_b  # Value from the second file (new)
        self.status = status
        self._parent = parent  # Renamed from 'parent'
        self._children = []  # Renamed from 'children'

    def appendChild(self, item):
        self._children.append(item)

    # --- ADD THE FOLLOWING METHODS TO MATCH TreeItem ---
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
            # Find our own index within the parent's children list
            return self._parent._children.index(self)
        return 0
    # --- END OF ADDED METHODS ---


def compare_dicts(dict_a: dict, dict_b: dict):
    """
    Recursively compares two dictionaries and returns a tree of DiffNode objects.
    """
    # The root DiffNode now has a key to match TreeItem's structure
    root_node = DiffNode("__root__")

    all_keys = sorted(list(set(dict_a.keys()) | set(dict_b.keys())))

    for key in all_keys:
        value_a = dict_a.get(key)
        value_b = dict_b.get(key)

        node = DiffNode(key, value_a, value_b, parent=root_node)

        if key not in dict_a:
            node.status = DiffStatus.ADDED
        elif key not in dict_b:
            node.status = DiffStatus.REMOVED
        elif value_a != value_b:
            node.status = DiffStatus.MODIFIED
            if isinstance(value_a, dict) and isinstance(value_b, dict):
                # The recursive call now returns a DiffNode, so we take its children
                child_root = compare_dicts(value_a, value_b)
                node._children = child_root._children  # Assign to _children
        # No UNCHANGED status needed in the diff tree, we will filter them later
        else:
            # For simplicity, we can skip unchanged nodes, or handle them
            # Here we will add them for completeness
            node.status = DiffStatus.UNCHANGED

        root_node.appendChild(node)

    return root_node