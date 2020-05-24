"""Contains the Poisoner class."""

from lib.logic.Character import Minion
from lib.logic.Effect import Poisoned
from lib.logic.charcreation import (
    evening_delete,
    generic_ongoing_effect,
    MorningTargeterMixin,
)


@evening_delete()
@generic_ongoing_effect
class _PoisonerPoison(Poisoned):
    """The Poisoner's poison."""

    pass


class Poisoner(Minion, MorningTargeterMixin):
    """The Poisoner."""

    name: str = "Poisoner"
    playtest: bool = False
    _MORNING_EFFECT = _PoisonerPoison
    _MORNING_TARGET_STRING = "poison"
