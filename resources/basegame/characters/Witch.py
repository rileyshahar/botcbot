"""Contains the Witch class."""

from lib.logic.Character import Minion


class Witch(Minion):
    """The Witch."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Witch"
        self.playtest = False
