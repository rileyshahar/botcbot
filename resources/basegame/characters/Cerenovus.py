"""Contains the Cerenovus class."""

from lib.logic.Character import Minion


class Cerenovus(Minion):
    """The Cerenovus."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Cerenovus"
        self.playtest = False
