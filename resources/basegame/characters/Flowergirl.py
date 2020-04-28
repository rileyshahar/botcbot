"""Contains the Flowergirl class."""

from lib.logic.Character import Townsfolk


class Flowergirl(Townsfolk):
    """The Flowergirl."""

    name: str = "Flowergirl"
    playtest: bool = False
