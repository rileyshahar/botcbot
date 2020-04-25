"""Contains the Washerwoman class."""

from lib.logic.Character import Townsfolk


class Washerwoman(Townsfolk):
    """The Washerwoman."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Washerwoman"
        self.playtest = False
