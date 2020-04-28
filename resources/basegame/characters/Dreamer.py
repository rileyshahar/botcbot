"""Contains the Dreamer class."""

from lib.logic.Character import Townsfolk


class Dreamer(Townsfolk):
    """The Dreamer."""

    name: str = "Dreamer"
    playtest: bool = False
