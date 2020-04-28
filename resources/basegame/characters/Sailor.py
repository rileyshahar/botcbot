"""Contains the Sailor class."""

from lib.logic.Character import Townsfolk


class Sailor(Townsfolk):
    """The Sailor."""

    name: str = "Sailor"
    playtest: bool = False
