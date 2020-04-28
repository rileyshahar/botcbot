"""Contains the Gossip class."""

from lib.logic.Character import Townsfolk


class Gossip(Townsfolk):
    """The Gossip."""

    name: str = "Gossip"
    playtest: bool = False
