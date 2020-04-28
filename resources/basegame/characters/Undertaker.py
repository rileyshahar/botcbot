"""Contains the Undertaker class."""

from lib.logic.Character import Townsfolk


class Undertaker(Townsfolk):
    """The Undertaker."""

    name: str = "Undertaker"
    playtest: bool = False
