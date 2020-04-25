"""Contains the TeaLady class."""

from lib.logic.Character import Townsfolk


class TeaLady(Townsfolk):
    """The Tea Lady."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Tea Lady"
        self.playtest = False
