"""Contains the Godfather class."""

from lib.logic.Character import Minion


class Godfather(Minion):
    """The Godfather."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Godfather"
        self.playtest = False
