"""Contains the Gambler class."""

from lib.logic.Character import Townsfolk


class Gambler(Townsfolk):
    """The Gambler."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Gambler"
        self.playtest = False
