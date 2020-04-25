"""Contains the Mutant class."""

from lib.logic.Character import Outsider


class Mutant(Outsider):
    """The Mutant."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Mutant"
        self.playtest = False
