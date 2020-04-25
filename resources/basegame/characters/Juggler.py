"""Contains the Juggler class."""

from lib.logic.Character import Townsfolk


class Juggler(Townsfolk):
    """The Juggler."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Juggler"
        self.playtest = False
