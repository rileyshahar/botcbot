"""Contains the Minstrel class."""

from lib.logic.Character import Townsfolk


class Minstrel(Townsfolk):
    """The Minstrel."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Minstrel"
        self.playtest = False
