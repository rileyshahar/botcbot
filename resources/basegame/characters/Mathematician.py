"""Contains the Mathematician class."""

from lib.logic.Character import Townsfolk


class Mathematician(Townsfolk):
    """The Mathematician."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Mathematician"
        self.playtest = False
