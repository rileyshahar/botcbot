"""Contains the Exorcist class."""

from lib.logic.Character import Townsfolk


class Exorcist(Townsfolk):
    """The Exorcist."""

    name: str = "Exorcist"
    playtest: bool = False
