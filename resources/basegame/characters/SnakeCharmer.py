"""Contains the SnakeCharmer class."""

from lib.logic.Character import Townsfolk


class SnakeCharmer(Townsfolk):
    """The Snake Charmer."""

    name: str = "Snake Charmer"
    playtest: bool = False
