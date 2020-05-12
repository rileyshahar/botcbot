"""Contains the Soldier class."""

from lib.logic.Character import Townsfolk
from lib.logic.tools import generic_ongoing_effect
from lib.logic.Effect import SafeFromDemon


class Soldier(Townsfolk):
    """The Soldier."""

    name: str = "Soldier"
    playtest: bool = False

    def __init__(self, parent):
        super().__init__(parent)
        self.default_effects += [generic_ongoing_effect(SafeFromDemon)]
        # TODO: generic ongoing effect isn't right here, it needs to disable on source
        # death, not delete
