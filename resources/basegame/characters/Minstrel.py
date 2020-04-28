"""Contains the Minstrel class."""

from lib.logic.Character import Townsfolk


class Minstrel(Townsfolk):
    """The Minstrel."""

    name: str = "Minstrel"
    playtest: bool = False
