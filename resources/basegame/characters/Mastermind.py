"""Contains the Mastermind class."""

from lib.logic.Character import Minion


class Mastermind(Minion):
    """The Mastermind."""

    name: str = "Mastermind"
    playtest: bool = False
