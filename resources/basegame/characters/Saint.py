"""Contains the Saint class."""

from lib.logic.Character import Outsider


class Saint(Outsider):
    """The Saint."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Saint"
        self.playtest = False
