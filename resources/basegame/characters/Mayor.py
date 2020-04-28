"""Contains the Mayor class."""

from lib.logic.Character import Townsfolk


class Mayor(Townsfolk):
    """The Mayor."""

    name: str = "Mayor"
    playtest: bool = False
