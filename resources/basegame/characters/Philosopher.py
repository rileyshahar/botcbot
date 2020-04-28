"""Contains the Philosopher class."""

from lib.logic.Character import Townsfolk


class Philosopher(Townsfolk):
    """The Philosopher."""

    name: str = "Philosopher"
    playtest: bool = False
