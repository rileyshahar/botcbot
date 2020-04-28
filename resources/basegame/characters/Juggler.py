"""Contains the Juggler class."""

from lib.logic.Character import Townsfolk


class Juggler(Townsfolk):
    """The Juggler."""

    name: str = "Juggler"
    playtest: bool = False
