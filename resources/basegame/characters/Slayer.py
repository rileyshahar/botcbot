"""Contains the Slayer class."""

from lib.logic.Character import Townsfolk


class Slayer(Townsfolk):
    """The Slayer."""

    name: str = "Slayer"
    playtest: bool = False
