"""Contains the Savant class."""

from lib.logic.Character import Townsfolk


class Savant(Townsfolk):
    """The Savant."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Savant"
        self.playtest = False
