"""Contains the Monk class."""

from lib.logic.Character import Townsfolk
from lib.logic.Effect import SafeFromDemon
from lib.logic.charcreation import (
    morning_delete,
    generic_ongoing_effect,
    MorningTargeterMixin,
)


@morning_delete()
@generic_ongoing_effect
class _MonkProtection(SafeFromDemon):
    """The Monk's protection."""

    pass


class Monk(Townsfolk, MorningTargeterMixin):
    """The Poisoner."""

    name: str = "Monk"
    playtest: bool = False
    _MORNING_EFFECT = _MonkProtection
    _MORNING_TARGET_STRING = "protect"
