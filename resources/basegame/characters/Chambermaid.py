"""Contains the Chambermaid class."""

from lib.logic.Character import Townsfolk


class Chambermaid(Townsfolk):
    """The Chambermaid."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Chambermaid"
        self.playtest = False
