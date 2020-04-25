"""Contains the Artist class."""

from lib.logic.Character import Townsfolk


class Artist(Townsfolk):
    """The Artist."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Artist"
        self.playtest = False
