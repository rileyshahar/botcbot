"""Contains the Artist class."""

from lib.logic.Character import Townsfolk


class Artist(Townsfolk):
    """The Artist."""

    name: str = "Artist"
    playtest: bool = False
