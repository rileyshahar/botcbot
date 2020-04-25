"""Contains the Zombuul class."""

from lib.logic.Character import Demon


class Zombuul(Demon):
    """The Zombuul."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Zombuul"
        self.playtest = False
