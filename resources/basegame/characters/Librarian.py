"""Contains the Librarian class."""

from lib.logic.Character import Townsfolk
from lib.logic.charcreation import SeesTwo


class Librarian(Townsfolk, SeesTwo):
    """The Librarian."""

    name: str = "Librarian"
    playtest: bool = False
    _SEES = "Outsider"
