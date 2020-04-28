"""Contains the Baron class."""

from lib.logic.Character import Minion


class Baron(Minion):
    """The Baron."""

    name: str = "Baron"
    playtest: bool = False
