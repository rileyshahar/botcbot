"""Contains the Mathematician class."""

from lib.logic.Character import Townsfolk


class Mathematician(Townsfolk):
    """The Mathematician."""

    name: str = "Mathematician"
    playtest: bool = False
