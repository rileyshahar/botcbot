"""Contains the Ravenkeeper class."""

from lib.logic.Character import Townsfolk


class Ravenkeeper(Townsfolk):
    """The Ravenkeeper."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Ravenkeeper"
        self.playtest = False
