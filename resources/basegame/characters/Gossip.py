"""Contains the Gossip class."""

from lib.logic.Character import Townsfolk


class Gossip(Townsfolk):
    """The Gossip."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Gossip"
        self.playtest = False
