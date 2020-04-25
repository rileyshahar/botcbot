"""Contains the Undertaker class."""

from lib.logic.Character import Townsfolk


class Undertaker(Townsfolk):
    """The Undertaker."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Undertaker"
        self.playtest = False
