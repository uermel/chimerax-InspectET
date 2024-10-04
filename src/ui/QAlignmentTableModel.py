from pathlib import Path
from typing import Any, Literal, Union

from qtpy.QtCore import QAbstractItemModel, QModelIndex, Qt
from qtpy.QtGui import QColor, QIcon
from qtpy.QtWidgets import QFileIconProvider

from cryoet_alignment.io.cryoet_data_portal.alignment import Alignment
from .AlignmentTable import AlignmentTableRoot, TableParams

class QAlignmentTableModel(QAbstractItemModel):
    def __init__(
        self,
        alignment: Alignment,
        parent=None,
    ):
        super().__init__(parent)
        self._icon_provider = QFileIconProvider()
        icons = Path(__file__).parent.parent / "icons"
        self._icon_eye_closed = QIcon(str(icons / "eye_closed.png"))
        self._icon_eye_open = QIcon(str(icons / "eye_open.png"))

        self._root = AlignmentTableRoot(alignment=alignment)

    def index(self, row: int, column: int, parent=QModelIndex()) -> Union[QModelIndex, None]:
        if not self.hasIndex(row, column, parent):
            return None

        parentItem = self._root if not parent.isValid() else parent.internalPointer()
        childItem = parentItem.child(row)

        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return None

    def item_index(self, item: TableParams) -> QModelIndex:
        childItem = item
        parentItem = childItem.parent

        if parentItem != self._root:
            return self.createIndex(parentItem.childIndex(), 0, parentItem)
        else:
            return QModelIndex()

    def parent(self, index: QModelIndex) -> Union[QModelIndex, None]:
        if not index.isValid():
            return None

        childItem = index.internalPointer()
        parentItem = childItem.parent

        if parentItem != self._root:
            return self.createIndex(parentItem.childIndex(), 0, parentItem)
        else:
            return QModelIndex()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        parentItem = self._root if not parent.isValid() else parent.internalPointer()

        return parentItem.childCount()

    def columnCount(self, parent: QModelIndex = QModelIndex()):
        return self._root.columnCount()

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if not index.isValid():
            return None

        item = index.internalPointer()

        if role == 0:
            return item.data(index.column())

    def hasChildren(self, parent: QModelIndex = ...) -> bool:
        parentItem = self._root if not parent.isValid() else parent.internalPointer()

        return parentItem.has_children  # parentItem.is_dir

    def headerData(self, section, orientation, role=...):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            if section == 0:
                return "Z"
            elif section == 1:
                return "TLT"
            elif section == 2:
                return "ROT"
            elif section == 3:
                return "TX"
            elif section == 4:
                return "TY"
            elif section == 5:
                return "ROTX"

    def flags(self, index: QModelIndex) -> Union[Qt.ItemFlag, None]:
        if not index.isValid():
            return None

        index.internalPointer()
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def update_all(self):
        self.layoutChanged.emit()
        self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount() - 1, self.columnCount() - 1))
