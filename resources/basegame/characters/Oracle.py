"""Contains the Oracle class."""

from lib.logic.Character import Townsfolk


class Oracle(Townsfolk):
    """The Oracle."""

    name: str = "Oracle"
    playtest: bool = False
