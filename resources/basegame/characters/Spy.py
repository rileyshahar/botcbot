"""Contains the Spy class."""

from lib.logic.Character import Minion


class Spy(Minion):
    """The Spy."""

    name: str = "Spy"
    playtest: bool = False
