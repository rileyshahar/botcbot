"""Contains the EvilTwin class."""

from lib.logic.Character import Minion


class EvilTwin(Minion):
    """The Evil Twin."""

    name: str = "Evil Twin"
    playtest: bool = False
