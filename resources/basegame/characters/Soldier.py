"""Contains the Soldier class."""

from lib.logic.Character import Townsfolk


class Soldier(Townsfolk):
    """The Soldier."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Soldier"
        self.playtest = False
