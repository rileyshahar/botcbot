"""Contains the Baron class."""

from lib.logic.Character import Minion


class Baron(Minion):
    """The Baron."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Baron"
        self.playtest = False
