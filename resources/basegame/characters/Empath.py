"""Contains the Empath class."""

from lib.logic.Character import Townsfolk


class Empath(Townsfolk):
    """The Empath."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Empath"
        self.playtest = False
