"""Contains the Seamstress class."""

from lib.logic.Character import Townsfolk


class Seamstress(Townsfolk):
    """The Seamstress."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Seamstress"
        self.playtest = False
