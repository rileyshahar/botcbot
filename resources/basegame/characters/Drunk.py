"""Contains the Drunk class."""

from lib.logic.Character import Outsider


class Drunk(Outsider):
    """The Drunk."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Drunk"
        self.playtest = False
