"""Contains the Flowergirl class."""

from lib.logic.Character import Townsfolk


class Flowergirl(Townsfolk):
    """The Flowergirl."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Flowergirl"
        self.playtest = False
