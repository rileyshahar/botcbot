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
    _morning_condition_string = "different"
    _morning_effect = _ButlerMaster
    _morning_target_string = "choose"
