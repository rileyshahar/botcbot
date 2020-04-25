"""Contains the Recluse class."""

from lib.logic.Character import Outsider


class Recluse(Outsider):
    """The Recluse."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Recluse"
        self.playtest = False
