"""Contains the Moonchild class."""

from lib.logic.Character import Outsider


class Moonchild(Outsider):
    """The Moonchild."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Moonchild"
        self.playtest = False
