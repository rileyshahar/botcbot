"""Contains the Empath class."""

from lib.logic.Character import Townsfolk


class Empath(Townsfolk):
    """The Empath."""

    name: str = "Empath"
    playtest: bool = False
