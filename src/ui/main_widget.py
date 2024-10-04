import os.path

from PyQt6.QtWidgets import QCheckBox
from Qt.QtCore import Qt, QObject, QModelIndex, Signal
from Qt.QtGui import QFont, QKeySequence
from Qt.QtWidgets import (
    QWidget,
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QSizePolicy,
    QComboBox,
    QLineEdit,
    QLabel,
    QTableView,
    QHeaderView,
    QGridLayout,
)

from typing import Dict, Optional, List

from chimerax.core.errors import UserError
from cryoet_alignment.io.imod import ImodAlignment
from cryoet_alignment.io.cryoet_data_portal import Alignment
from cryoet_alignment.io.aretomo3 import AreTomo3ALN

from .QAlignmentTableModel import QAlignmentTableModel
from ..core.alignment import create_alignment_objects
from ..core.alignment import apply_alignment
from .LabelEditSlider import LabelEditSlider
from ..util.s3 import imod_from_s3, aretomo3_from_s3, cdp_from_s3

PATH_PLACEHOLDER = "Path / S3 URI"
BASENAME_PLACEHOLDER = "Basename / S3 URI Basename"


class MainWidget(QWidget):

    def __init__(
        self,
        session,
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent=parent)

        self.session = session

        self._build()
        self._connect()

    def _build(self):

        self._input_group = QGroupBox("Input")
        self._input_layout = QVBoxLayout()

        # Input Alignment Type
        self._inputs_layout = QGridLayout()

        self._input_ali_label = QLabel("Alignment Type:")
        self._input_ali_combo = QComboBox()
        self._input_ali_combo.addItem("CryoET Data Portal")
        self._input_ali_combo.addItem("IMOD")
        self._input_ali_combo.addItem("AreTomo3")
        self._input_ali_combo.setCurrentIndex(2)

        self._inputs_layout.addWidget(self._input_ali_label, 0, 0, 1, 1, Qt.AlignmentFlag.AlignLeft)
        self._inputs_layout.addWidget(self._input_ali_combo, 0, 1, 1, 3)

        # Input Alignment File
        self._input_ali_file_label = QLabel("Alignment Path:")
        self._input_ali_file_edit = QLineEdit("")
        self._input_ali_file_edit.setPlaceholderText(PATH_PLACEHOLDER)

        self._inputs_layout.addWidget(self._input_ali_file_label, 1, 0, 1, 1, Qt.AlignmentFlag.AlignLeft)
        self._inputs_layout.addWidget(self._input_ali_file_edit, 1, 1, 1, 3)

        # Vol Dim
        self._vol_dim_check = QCheckBox("Use Vol Dims:")
        self._vol_dim_check.setChecked(True)
        self._input_vol_dim_x = QLineEdit("10000")
        self._input_vol_dim_y = QLineEdit("10000")
        self._input_vol_dim_z = QLineEdit("4000")
        self._input_vol_dim_x.setPlaceholderText("X")
        self._input_vol_dim_y.setPlaceholderText("Y")
        self._input_vol_dim_z.setPlaceholderText("Z")
        self._input_vol_dim_x.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum))
        self._input_vol_dim_y.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum))
        self._input_vol_dim_z.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum))

        self._inputs_layout.addWidget(self._vol_dim_check, 2, 0, 1, 1, Qt.AlignmentFlag.AlignLeft)
        self._inputs_layout.addWidget(self._input_vol_dim_x, 2, 1, 1, 1)
        self._inputs_layout.addWidget(self._input_vol_dim_y, 2, 2, 1, 1)
        self._inputs_layout.addWidget(self._input_vol_dim_z, 2, 3, 1, 1)

        # Input tilt series
        self._input_ts_label = QLabel("Tilt Series:")
        self._input_ts_edit = QLineEdit()
        self._input_ts_edit.setPlaceholderText("Path [Optional]")
        self._input_ts_edit.setEnabled(False)

        self._inputs_layout.addWidget(self._input_ts_label, 3, 0, 1, 1, Qt.AlignmentFlag.AlignLeft)
        self._inputs_layout.addWidget(self._input_ts_edit, 3, 1, 1, 3)

        # Input volume
        self._input_vol_label = QLabel("Volume:")
        self._input_vol_edit = QLineEdit()
        self._input_vol_edit.setPlaceholderText("Path [Optional]")
        self._input_vol_edit.setEnabled(False)

        self._inputs_layout.addWidget(self._input_vol_label, 4, 0, 1, 2, Qt.AlignmentFlag.AlignLeft)
        self._inputs_layout.addWidget(self._input_vol_edit, 4, 1, 1, 3)

        # Load button
        self._load_button = QPushButton("Load")
        self._input_layout.addWidget(
            self._load_button,
        )

        self._inputs_layout.addWidget(self._load_button, 5, 0, 1, 4, Qt.AlignmentFlag.AlignCenter)

        # Set final layout
        self._input_group.setLayout(self._inputs_layout)
        self._input_group.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum))

        # Alignment Table
        self._alignment_group = QGroupBox("Alignment")
        self.ali_table = QTableView()
        self.ali_table.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        )
        self.ali_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.ali_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        header = self.ali_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self._ali_layout = QVBoxLayout()
        self._ali_layout.addWidget(self.ali_table)

        self._slide_layout = QHBoxLayout()
        self._play_button = QPushButton("▶")
        self._play_button.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum))
        self._slider = LabelEditSlider([0, 1], "Z", 0.8, 1)
        self._slide_layout.addWidget(self._play_button)
        self._slide_layout.addWidget(self._slider)
        self._ali_layout.addLayout(self._slide_layout)
        self._alignment_group.setLayout(self._ali_layout)

        # Main layout
        self._layout = QVBoxLayout()
        self._layout.addWidget(self._input_group)
        self._layout.addWidget(self._alignment_group)
        self.setLayout(self._layout)

    def _connect(self):
        self._load_button.clicked.connect(self._load_alignment)
        self.ali_table.clicked.connect(self._apply_alignment)
        self._slider.valueChanged.connect(self._apply_alignment_int)
        self._input_ali_combo.currentIndexChanged.connect(self._ali_type_changed)
        self._vol_dim_check.stateChanged.connect(self._input_type_changed)
        self._play_button.clicked.connect(self._play)

    def _play(self):
        from chimerax.core.commands import run

        run(self.session, "inspectet play framesPerView 10 loopNumber 1")

    def _update_ui(self, checkbox: bool = True):
        enable_paths = True

        if self._input_ali_combo.currentText() == "IMOD":
            enable_paths = False
            self._input_ali_file_edit.setPlaceholderText(BASENAME_PLACEHOLDER)

        elif self._input_ali_combo.currentText() == "AreTomo3":
            enable_paths = not checkbox
            self._input_ali_file_edit.setPlaceholderText(PATH_PLACEHOLDER)

        elif self._input_ali_combo.currentText() == "CryoET Data Portal":
            enable_paths = not checkbox
            self._input_ali_file_edit.setPlaceholderText(PATH_PLACEHOLDER)

        print("checkbox", checkbox)
        if checkbox:
            self._input_vol_dim_x.setEnabled(True)
            self._input_vol_dim_y.setEnabled(True)
            self._input_vol_dim_z.setEnabled(True)
            self._input_vol_dim_x.setText("10000")
            self._input_vol_dim_y.setText("10000")
            self._input_vol_dim_z.setText("4000")
        else:
            self._input_vol_dim_x.setEnabled(False)
            self._input_vol_dim_y.setEnabled(False)
            self._input_vol_dim_z.setEnabled(False)
            self._input_vol_dim_x.setText("")
            self._input_vol_dim_y.setText("")
            self._input_vol_dim_z.setText("")

        if enable_paths:
            self._input_vol_edit.setEnabled(True)
            self._input_ts_edit.setEnabled(True)
            self._input_vol_edit.setText("")
            self._input_ts_edit.setText("")
            self._input_vol_edit.setPlaceholderText("Path [Optional]")
            self._input_ts_edit.setPlaceholderText("Path [Optional]")
        else:
            self._input_vol_edit.setText("")
            self._input_ts_edit.setText("")
            self._input_ts_edit.setEnabled(False)
            self._input_vol_edit.setEnabled(False)

    def _ali_type_changed(self, index: int):
        self._input_ali_file_edit.setText("")
        self._vol_dim_check.setChecked(False)
        self._update_ui(checkbox=False)

    def _input_type_changed(self, state: int):
        print(state)
        if state == 2:
            self._update_ui(True)
        else:
            self._update_ui(False)

    def _load_alignment(self):
        file = self._input_ali_file_edit.text()

        if not file:
            return

        # Vol Dim
        if self._vol_dim_check.isChecked():
            vol_x = float(self._input_vol_dim_x.text())
            vol_y = float(self._input_vol_dim_y.text())
            vol_z = float(self._input_vol_dim_z.text())
        else:
            vol_x = None
            vol_y = None
            vol_z = None

        # Vol File
        vol_file = self._input_vol_edit.text()
        if vol_file == "":
            vol_file = None

        # TS File
        ts_file = self._input_ts_edit.text()
        if ts_file == "":
            ts_file = None

        # Load alignment file
        type = self._input_ali_combo.currentText()
        if type == "CryoET Data Portal":

            if "s3://" in file:
                ali = cdp_from_s3(file)
            else:
                ali = Alignment.from_file(file)

            from chimerax.geometry import rotation

            self.session.inspectet.additional_rotation = rotation((1, 0, 0), 0)
            self.session.inspectet.initial_coord_order = [0, 1, 2]
            self.session.inspectet.current_alignment = ali

        elif type == "IMOD":
            # imod_ali = ImodAlignment.read(base_name=file)
            if "s3://" in file:
                imod_ali = imod_from_s3(file)
                if vol_x is not None:
                    ali = Alignment.from_imod(imod_ali, vol_size=(vol_x, vol_y, vol_z))
                else:
                    ali = Alignment.from_imod(imod_ali)
            else:
                ali = Alignment.from_imod_basename(file)

            if os.path.exists(f"{file}_full_rec.mrc"):
                vol_file = f"{file}_full_rec.mrc"

            if vol_file is None and vol_x is None:
                raise UserError("No *_full_rec.mrc found at IMOD basename and no vol dims provided.")

            if os.path.exists(f"{file}.mrc"):
                ts_file = f"{file}.mrc"

            from chimerax.geometry import rotation

            self.session.inspectet.additional_rotation = rotation((1, 0, 0), -90)
            self.session.inspectet.initial_coord_order = [0, 2, 1]
            self.session.inspectet.current_alignment = ali

        elif type == "AreTomo3":
            if vol_file is None and vol_x is None:
                raise UserError("Please provide volume dimensions or a volume file.")

            if "s3://" in file:
                ali = aretomo3_from_s3(file)
            else:
                ali = AreTomo3ALN.from_file(file)

            if vol_file is None:
                ali = Alignment.from_aretomo3(ali, vol_size=(vol_x, vol_y, vol_z))
            else:
                ali = Alignment.from_aretomo3(ali, vol=vol_file)

            from chimerax.geometry import rotation

            self.session.inspectet.additional_rotation = rotation((1, 0, 0), 0)
            self.session.inspectet.initial_coord_order = [0, 1, 2]
            self.session.inspectet.current_alignment = ali
        else:
            return

        # Load alignment into table
        model = QAlignmentTableModel(ali)
        self.ali_table.setModel(model)

        # Render alignment
        create_alignment_objects(self.session, ali, ali.per_section_alignment_parameters[0], vol_file, ts_file)

        # Set slider range
        self._slider.set_range((0, len(ali.per_section_alignment_parameters) - 1), 0)

    def _apply_alignment(self, index: QModelIndex):
        if self.session.inspectet.current_alignment is None:
            return

        if not index.isValid():
            return

        item = index.internalPointer()

        if item is not None:
            apply_alignment(self.session, self.session.inspectet.current_alignment, item.params)

    def _apply_alignment_int(self, z: int):
        if self.session.inspectet.current_alignment is None:
            return

        model = self.ali_table.model()
        index = model.index(int(z), int(0))
        self._apply_alignment(index)
        self.ali_table.setCurrentIndex(index)
