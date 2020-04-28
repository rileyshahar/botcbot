"""Contains the Innkeeper class."""

from lib.logic.Character import Townsfolk


class Innkeeper(Townsfolk):
    """The Innkeeper."""

    name: str = "Innkeeper"
    playtest: bool = False
