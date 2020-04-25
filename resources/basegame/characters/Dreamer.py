"""Contains the Dreamer class."""

from lib.logic.Character import Townsfolk


class Dreamer(Townsfolk):
    """The Dreamer."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Dreamer"
        self.playtest = False
