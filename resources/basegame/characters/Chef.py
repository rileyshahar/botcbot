"""Contains the Chef class."""

from lib.logic.Character import Townsfolk


class Chef(Townsfolk):
    """The Chef."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Chef"
        self.playtest = False
