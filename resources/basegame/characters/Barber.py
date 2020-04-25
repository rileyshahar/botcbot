"""Contains the Barber class."""

from lib.logic.Character import Outsider


class Barber(Outsider):
    """The Barber."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Barber"
        self.playtest = False
