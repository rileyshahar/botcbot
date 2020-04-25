"""Contains the DevilSAdvocate class."""

from lib.logic.Character import Minion


class DevilSAdvocate(Minion):
    """The Devil's Advocate."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Devil's Advocate"
        self.playtest = False
