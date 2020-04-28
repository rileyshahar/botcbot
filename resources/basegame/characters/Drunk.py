"""Contains the Drunk class."""

from lib.logic.Character import Outsider


class Drunk(Outsider):
    """The Drunk."""

    name: str = "Drunk"
    playtest: bool = False
