"""Contains the Sailor class."""

from lib.logic.Character import Townsfolk


class Sailor(Townsfolk):
    """The Sailor."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Sailor"
        self.playtest = False
