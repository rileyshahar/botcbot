"""Contains the Assassin class."""

from lib.logic.Character import Minion


class Assassin(Minion):
    """The Assassin."""

    name: str = "Assassin"
    playtest: bool = False
