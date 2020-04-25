"""Contains the FortuneTeller class."""

from lib.logic.Character import Townsfolk


class FortuneTeller(Townsfolk):
    """The Fortune Teller."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Fortune Teller"
        self.playtest = False
