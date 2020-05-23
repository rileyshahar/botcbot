"""Contains the Washerwoman class."""

from lib.logic.Character import Townsfolk
from lib.logic.charcreation import SeesTwo


class Washerwoman(Townsfolk, SeesTwo):
    """The Washerwoman."""

    name: str = "Washerwoman"
    playtest: bool = False
    _SEES = "Townsfolk"
