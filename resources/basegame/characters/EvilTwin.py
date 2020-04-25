"""Contains the EvilTwin class."""

from lib.logic.Character import Minion


class EvilTwin(Minion):
    """The Evil Twin."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Evil Twin"
        self.playtest = False
