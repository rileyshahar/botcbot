"""Contains the Gunslinger class."""

from lib.logic.Character import Traveler


class Gunslinger(Traveler):
    """The Gunslinger."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Gunslinger"
