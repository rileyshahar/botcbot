"""Contains the Sage class."""

from lib.logic.Character import Townsfolk


class Sage(Townsfolk):
    """The Sage."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Sage"
        self.playtest = False
