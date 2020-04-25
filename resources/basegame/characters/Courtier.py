"""Contains the Courtier class."""

from lib.logic.Character import Townsfolk


class Courtier(Townsfolk):
    """The Courtier."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Courtier"
        self.playtest = False
