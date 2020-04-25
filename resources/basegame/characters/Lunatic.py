"""Contains the Lunatic class."""

from lib.logic.Character import Outsider


class Lunatic(Outsider):
    """The Lunatic."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Lunatic"
        self.playtest = False
