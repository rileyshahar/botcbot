"""Contains the Goon class."""

from lib.logic.Character import Outsider


class Goon(Outsider):
    """The Goon."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Goon"
        self.playtest = False
