"""Contains the TownCrier class."""

from lib.logic.Character import Townsfolk


class TownCrier(Townsfolk):
    """The Town Crier."""

    name: str = "Town Crier"
    playtest: bool = False
