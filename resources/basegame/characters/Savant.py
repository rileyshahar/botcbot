"""Contains the Savant class."""

from lib.logic.Character import Townsfolk


class Savant(Townsfolk):
    """The Savant."""

    name: str = "Savant"
    playtest: bool = False
