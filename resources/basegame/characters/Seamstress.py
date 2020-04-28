"""Contains the Seamstress class."""

from lib.logic.Character import Townsfolk


class Seamstress(Townsfolk):
    """The Seamstress."""

    name: str = "Seamstress"
    playtest: bool = False
