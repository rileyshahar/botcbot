"""Contains the Grandmother class."""

from lib.logic.Character import Townsfolk


class Grandmother(Townsfolk):
    """The Grandmother."""

    name: str = "Grandmother"
    playtest: bool = False
