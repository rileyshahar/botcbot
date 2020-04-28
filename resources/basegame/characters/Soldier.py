"""Contains the Soldier class."""

from lib.logic.Character import Townsfolk


class Soldier(Townsfolk):
    """The Soldier."""

    name: str = "Soldier"
    playtest: bool = False
