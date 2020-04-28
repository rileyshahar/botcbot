"""Contains the Chef class."""

from lib.logic.Character import Townsfolk


class Chef(Townsfolk):
    """The Chef."""

    name: str = "Chef"
    playtest: bool = False
