"""Contains the Clockmaker class."""

from lib.logic.Character import Townsfolk


class Clockmaker(Townsfolk):
    """The Clockmaker."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Clockmaker"
        self.playtest = False
