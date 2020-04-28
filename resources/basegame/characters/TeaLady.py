"""Contains the TeaLady class."""

from lib.logic.Character import Townsfolk


class TeaLady(Townsfolk):
    """The Tea Lady."""

    name: str = "Tea Lady"
    playtest: bool = False
