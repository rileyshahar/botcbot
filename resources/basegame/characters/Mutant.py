"""Contains the Mutant class."""

from lib.logic.Character import Outsider


class Mutant(Outsider):
    """The Mutant."""

    name: str = "Mutant"
    playtest: bool = False
