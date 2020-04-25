"""Contains the Innkeeper class."""

from lib.logic.Character import Townsfolk


class Innkeeper(Townsfolk):
    """The Innkeeper."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Innkeeper"
        self.playtest = False
