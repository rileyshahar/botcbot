"""Contains the Grandmother class."""

from lib.logic.Character import Townsfolk


class Grandmother(Townsfolk):
    """The Grandmother."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Grandmother"
        self.playtest = False
