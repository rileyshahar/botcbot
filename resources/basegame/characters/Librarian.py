"""Contains the Librarian class."""

from lib.logic.Character import Townsfolk


class Librarian(Townsfolk):
    """The Librarian."""

    name: str = "Librarian"
    playtest: bool = False
