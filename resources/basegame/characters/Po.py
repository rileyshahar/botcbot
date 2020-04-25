"""Contains the Po class."""

from lib.logic.Character import Demon


class Po(Demon):
    """The Po."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Po"
        self.playtest = False
