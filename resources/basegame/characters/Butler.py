"""Contains the Butler class."""

from lib.logic.Character import Outsider


class Butler(Outsider):
    """The Butler."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Butler"
        self.playtest = False
