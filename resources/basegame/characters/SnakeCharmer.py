"""Contains the SnakeCharmer class."""

from lib.logic.Character import Townsfolk


class SnakeCharmer(Townsfolk):
    """The Snake Charmer."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Snake Charmer"
        self.playtest = False
