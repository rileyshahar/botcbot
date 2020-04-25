"""Contains the Assassin class."""

from lib.logic.Character import Minion


class Assassin(Minion):
    """The Assassin."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Assassin"
        self.playtest = False
