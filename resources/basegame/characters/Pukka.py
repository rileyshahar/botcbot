"""Contains the Pukka class."""

from lib.logic.Character import Demon


class Pukka(Demon):
    """The Pukka."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Pukka"
        self.playtest = False
