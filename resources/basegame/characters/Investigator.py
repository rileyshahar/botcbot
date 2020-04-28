"""Contains the Investigator class."""

from lib.logic.Character import Townsfolk


class Investigator(Townsfolk):
    """The Investigator."""

    name: str = "Investigator"
    playtest: bool = False
