"""Contains the Butler class."""

from lib.logic.Character import Outsider
from lib.logic.Effect import Effect
from lib.logic.charcreation import MorningTargeterMixin


class _ButlerMaster(Effect):
    _name = "Master"


class Butler(Outsider, MorningTargeterMixin):
    """The Butler."""

    name: str = "Butler"
    playtest: bool = False
    _MORNING_CONDITION_STRING = "different"
    _MORNING_EFFECT = _ButlerMaster
    _MORNING_TARGET_STRING = "choose"
