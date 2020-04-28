"""Contains the Courtier class."""

from lib.logic.Character import Townsfolk


class Courtier(Townsfolk):
    """The Courtier."""

    name: str = "Courtier"
    playtest: bool = False
