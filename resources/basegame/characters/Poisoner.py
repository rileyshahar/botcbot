"""Contains the Poisoner class."""
from typing import Tuple, List

from lib.logic.Character import Minion
from lib.logic.Effect import Poisoned
from lib.logic.Player import Player
from lib.logic.tools import (
    if_functioning,
    evening_delete,
    generic_ongoing_effect,
    add_targeted_effect,
)


@evening_delete()
@generic_ongoing_effect
class _PoisonerPoison(Poisoned):
    """The Poisoner's poison."""

    pass


class Poisoner(Minion):
    """The Poisoner."""

    name: str = "Poisoner"
    playtest: bool = False

    @if_functioning(True)
    async def morning(
        self, ctx, enabled=True, epithet_string=""
    ) -> Tuple[List[Player], List[str]]:
        """Apply the Poisoner's poison to a chosen target."""
        return await add_targeted_effect(
            self, ctx, _PoisonerPoison, "poison", enabled=enabled
        )
