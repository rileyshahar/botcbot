"""Contains the Investigator class."""

from lib.logic.Character import Townsfolk
from lib.logic.charcreation import SeesTwo


class Investigator(Townsfolk, SeesTwo):
    """The Investigator."""

    name: str = "Investigator"
    playtest: bool = False
    _SEES = "Minion"
