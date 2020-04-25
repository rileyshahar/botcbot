"""Contains the Investigator class."""

from lib.logic.Character import Townsfolk


class Investigator(Townsfolk):
    """The Investigator."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Investigator"
        self.playtest = False
