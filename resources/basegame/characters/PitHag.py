"""Contains the PitHag class."""

from lib.logic.Character import Minion


class PitHag(Minion):
    """The Pit-Hag."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Pit-Hag"
        self.playtest = False
