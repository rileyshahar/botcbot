"""Contains the Spy class."""

from lib.logic.Character import Minion


class Spy(Minion):
    """The Spy."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Spy"
        self.playtest = False
