"""Contains the Philosopher class."""

from lib.logic.Character import Townsfolk


class Philosopher(Townsfolk):
    """The Philosopher."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Philosopher"
        self.playtest = False
