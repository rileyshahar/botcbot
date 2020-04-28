"""Contains the Goon class."""

from lib.logic.Character import Outsider


class Goon(Outsider):
    """The Goon."""

    name: str = "Goon"
    playtest: bool = False
