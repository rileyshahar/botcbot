"""Contains the Gambler class."""

from lib.logic.Character import Townsfolk


class Gambler(Townsfolk):
    """The Gambler."""

    name: str = "Gambler"
    playtest: bool = False
