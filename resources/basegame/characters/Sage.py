"""Contains the Sage class."""

from lib.logic.Character import Townsfolk


class Sage(Townsfolk):
    """The Sage."""

    name: str = "Sage"
    playtest: bool = False
