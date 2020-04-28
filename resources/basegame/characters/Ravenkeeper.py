"""Contains the Ravenkeeper class."""

from lib.logic.Character import Townsfolk


class Ravenkeeper(Townsfolk):
    """The Ravenkeeper."""

    name: str = "Ravenkeeper"
    playtest: bool = False
