# General
import os.path
from sys import platform

# ChimeraX
from chimerax.core.tools import ToolInstance
from chimerax.ui import MainToolWindow

# Qt
from Qt.QtGui import QFont
from Qt.QtWidgets import (
    QVBoxLayout,
)

from .ui.main_widget import MainWidget


class InspectETTool(ToolInstance):
    # Does this instance persist when session closes
    SESSION_ENDURING = False
    # We do save/restore in sessions
    SESSION_SAVE = False
    # Let ChimeraX know about our help page
    # help = "help:user/tools/artiax.html"

    # ==============================================================================
    # Instance Initialization ======================================================
    # ==============================================================================

    def __init__(self, session, tool_name):
        # 'session'     - chimerax.core.session.Session instance
        # 'tool_name'   - string

        # Initialize base class
        super().__init__(session, tool_name)

        # Display Name
        self.display_name = "InspectET"

        # Store self in session
        session.inspectet = self

        # Set the font
        if platform == "darwin":
            self.font = QFont("Arial", 10)
        else:
            self.font = QFont("Arial", 7)

        # UI
        self.tool_window = MainToolWindow(self, close_destroys=True)
        self._build_ui()

        self.axes_model = None
        self.volume_model = None
        self.raw_tiltseries = None
        self.aligned_tiltseries = None

        from chimerax.geometry import rotation

        self.additional_rotation = rotation((1, 0, 0), 0)
        self.initial_coord_order = [0, 1, 2]
        self.current_alignment = None

        from chimerax.core.commands import run

        run(session, "camera ortho")
        run(session, "lighting depthCue false")

    def _build_ui(self):
        tw = self.tool_window

        self._layout = QVBoxLayout()
        self._mw = MainWidget(self.session)
        self._layout.addWidget(self._mw)

        tw.ui_area.setLayout(self._layout)
        tw.manage("left")
