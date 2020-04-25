"""Contains the Mastermind class."""

from lib.logic.Character import Minion


class Mastermind(Minion):
    """The Mastermind."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Mastermind"
        self.playtest = False
