"""Contains the Sweetheart class."""

from lib.logic.Character import Outsider


class Sweetheart(Outsider):
    """The Sweetheart."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Sweetheart"
        self.playtest = False
