"""Contains the Klutz class."""

from lib.logic.Character import Outsider


class Klutz(Outsider):
    """The Klutz."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Klutz"
        self.playtest = False
