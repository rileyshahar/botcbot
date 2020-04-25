"""Contains the TownCrier class."""

from lib.logic.Character import Townsfolk


class TownCrier(Townsfolk):
    """The Town Crier."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Town Crier"
        self.playtest = False
