"""Contains the Godfather class."""

from lib.logic.Character import Minion


class Godfather(Minion):
    """The Godfather."""

    name: str = "Godfather"
    playtest: bool = False
