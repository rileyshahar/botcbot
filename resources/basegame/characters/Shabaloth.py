"""Contains the Shabaloth class."""

from lib.logic.Character import Demon


class Shabaloth(Demon):
    """The Shabaloth."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Shabaloth"
        self.playtest = False
