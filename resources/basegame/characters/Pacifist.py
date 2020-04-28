"""Contains the Pacifist class."""

from lib.logic.Character import Townsfolk


class Pacifist(Townsfolk):
    """The Pacifist."""

    name: str = "Pacifist"
    playtest: bool = False
