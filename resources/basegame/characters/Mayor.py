"""Contains the Mayor class."""

from lib.logic.Character import Townsfolk


class Mayor(Townsfolk):
    """The Mayor."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Mayor"
        self.playtest = False
