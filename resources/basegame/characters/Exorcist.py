"""Contains the Exorcist class."""

from lib.logic.Character import Townsfolk


class Exorcist(Townsfolk):
    """The Exorcist."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Exorcist"
        self.playtest = False
