"""Contains the Slayer class."""

from lib.logic.Character import Townsfolk


class Slayer(Townsfolk):
    """The Slayer."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Slayer"
        self.playtest = False
