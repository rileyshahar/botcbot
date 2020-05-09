"""Contains the Poisoner class."""
from typing import Tuple, List

from lib.logic.Character import Minion
from lib.logic.Effect import Poisoned
from lib.logic.Player import Player
from lib.logic.tools import (
    if_functioning,
    evening_delete,
    generic_ongoing_effect,
    select_target,
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
        target = await select_target(
            ctx, f"Who did {self.parent.formatted_epithet(epithet_string)}, poison?"
        )
        if target:
            effect = target.add_effect(ctx, _PoisonerPoison, self.parent)
            if not enabled:
                effect.disable(ctx)
        return [], []
