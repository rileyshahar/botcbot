"""Contains the FortuneTeller class."""

from lib.logic.Character import Townsfolk


class FortuneTeller(Townsfolk):
    """The Fortune Teller."""

    name: str = "Fortune Teller"
    playtest: bool = False
