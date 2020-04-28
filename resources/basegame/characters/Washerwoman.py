"""Contains the Washerwoman class."""

from lib.logic.Character import Townsfolk


class Washerwoman(Townsfolk):
    """The Washerwoman."""

    name: str = "Washerwoman"
    playtest: bool = False
