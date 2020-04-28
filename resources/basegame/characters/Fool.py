"""Contains the Fool class."""

from lib.logic.Character import Townsfolk


class Fool(Townsfolk):
    """The Fool."""

    name: str = "Fool"
    playtest: bool = False
