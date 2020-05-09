"""Contains the Monk class."""
from typing import Tuple, List

from lib.logic.Character import Townsfolk
from lib.logic.Effect import SafeFromDemon
from lib.logic.Player import Player
from lib.logic.tools import (
    if_functioning,
    morning_delete,
    generic_ongoing_effect,
    select_target,
)
from lib.typings.context import Context


@morning_delete()
@generic_ongoing_effect
class _MonkProtection(SafeFromDemon):
    """The Monk's protection."""

    pass


class Monk(Townsfolk):
    """The Monk."""

    name: str = "Monk"
    playtest: bool = False

    @if_functioning(True)
    async def morning(
        self, ctx: Context, enabled: bool = True, epithet_string: str = ""
    ) -> Tuple[List["Player"], List[str]]:
        """Apply the Monk's protection to a chosen target."""
        target = await select_target(
            ctx, f"Who did {self.parent.formatted_epithet(epithet_string)}, protect?"
        )
        if target:
            effect = target.add_effect(ctx, _MonkProtection, self.parent)
            if not enabled:
                effect.disable(ctx)
        return [], []
