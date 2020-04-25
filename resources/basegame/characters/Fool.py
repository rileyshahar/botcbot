"""Contains the Fool class."""

from lib.logic.Character import Townsfolk


class Fool(Townsfolk):
    """The Fool."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Fool"
        self.playtest = False
