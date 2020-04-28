"""Contains the PitHag class."""

from lib.logic.Character import Minion


class PitHag(Minion):
    """The Pit-Hag."""

    name: str = "Pit-Hag"
    playtest: bool = False
