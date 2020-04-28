"""Contains the Chambermaid class."""

from lib.logic.Character import Townsfolk


class Chambermaid(Townsfolk):
    """The Chambermaid."""

    name: str = "Chambermaid"
    playtest: bool = False
