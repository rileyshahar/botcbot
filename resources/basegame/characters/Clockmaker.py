"""Contains the Clockmaker class."""

from lib.logic.Character import Townsfolk


class Clockmaker(Townsfolk):
    """The Clockmaker."""

    name: str = "Clockmaker"
    playtest: bool = False
