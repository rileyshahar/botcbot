"""Contains the Witch class."""

from lib.logic.Character import Minion


class Witch(Minion):
    """The Witch."""

    name: str = "Witch"
    playtest: bool = False
