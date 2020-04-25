"""Contains the Pacifist class."""

from lib.logic.Character import Townsfolk


class Pacifist(Townsfolk):
    """The Pacifist."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Pacifist"
        self.playtest = False
