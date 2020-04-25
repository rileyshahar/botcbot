"""Contains the Librarian class."""

from lib.logic.Character import Townsfolk


class Librarian(Townsfolk):
    """The Librarian."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Librarian"
        self.playtest = False
