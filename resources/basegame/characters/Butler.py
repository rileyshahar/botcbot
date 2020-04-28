"""Contains the Butler class."""

from lib.logic.Character import Outsider


class Butler(Outsider):
    """The Butler."""

    name: str = "Butler"
    playtest: bool = False
