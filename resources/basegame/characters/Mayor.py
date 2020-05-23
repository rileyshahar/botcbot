"""Contains the Mayor class."""

from lib.logic.Character import Townsfolk


class Mayor(Townsfolk):
    """The Mayor."""

    name: str = "Mayor"
    playtest: bool = False

    # TODO: mayor bounces
    # we don't have each access to character death on this scope
    # this needs to be done after we move to a C-style events setup
