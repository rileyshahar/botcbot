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


# TODO: the problem right now is itll ask the poisoner who to target
# even if they cant use their ability because of death
# the if_functioning check needs to happen sometime earlier
# before morning_call is called


class Poisoner(Minion, MorningTargeterMixin):
    """The Poisoner."""

    name: str = "Poisoner"
    playtest: bool = False
    _morning_effect = _PoisonerPoison
    _morning_target_string = "poison"
