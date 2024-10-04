from typing import Callable, Tuple, Type, Union

from cryoet_alignment.io.cryoet_data_portal.alignment import Alignment, PerSectionAlignmentParameters

class TableParams:
    CopickClass = None

    def __init__(self, params: PerSectionAlignmentParameters, parent: "EntityTableRoot"):
        self.params = params
        self.parent = parent
        self.is_active = False
        self.has_children = False

    def child(self, row) -> None:
        return None

    def childCount(self) -> int:
        return 0

    def childIndex(self) -> Union[int, None]:
        return self.parent.psaps.index(self.params)

    def data(self, column: int) -> str:
        if column == 0:
            return self.params.z_index
        elif column == 1:
            return f"{self.params.tilt_angle:.2f}"
        elif column == 2:
            return f"{self.params.tilt_axis_rotation:.2f}"
        elif column == 3:
            return f"{self.params.x_offset:.2f}"
        elif column == 4:
            return f"{self.params.y_offset:.2f}"
        elif column == 5:
            return f"{self.params.volume_x_rotation:.2f}"


    # def color(self) -> Tuple[int, ...]:
    #     return tuple(self.entity.color)

    def columnCount(self) -> int:
        return 6


class AlignmentTableRoot:
    def __init__(self, alignment: Alignment):
        self.alignment = alignment
        self.psaps = alignment.per_section_alignment_parameters
        self._children = None
        self.parent = None
        self.is_active = False

    @property
    def children(self):
        if self._children is None:
            self._children = [TableParams(psap, self) for psap in self.psaps]

        return self._children

    def child(self, row) -> TableParams:
        return self.children[row]

    def childCount(self) -> int:
        return len(self.children)

    def childIndex(self) -> Union[int, None]:
        return None

    def data(self, column: int) -> str:
        if column == 0:
            return "Z"
        elif column == 1:
            return "TLT"
        elif column == 2:
            return "ROT"
        elif column == 3:
            return "TX"
        elif column == 4:
            return "TY"
        elif column == 5:
            return "ROTX"

    def columnCount(self) -> int:
        return 6

    def get_item(self, params: PerSectionAlignmentParameters) -> Union[None, TableParams]:
        for child in self.children:
            if child.params == params:
                return child
        return None
