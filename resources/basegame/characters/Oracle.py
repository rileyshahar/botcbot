"""Contains the Oracle class."""

from lib.logic.Character import Townsfolk


class Oracle(Townsfolk):
    """The Oracle."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Oracle"
        self.playtest = False
