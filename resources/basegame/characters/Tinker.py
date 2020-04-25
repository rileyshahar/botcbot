"""Contains the Tinker class."""

from lib.logic.Character import Outsider


class Tinker(Outsider):
    """The Tinker."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Tinker"
        self.playtest = False
