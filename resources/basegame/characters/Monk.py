"""Contains the Monk class."""

from lib.logic.Character import Townsfolk
from lib.logic.Effect import SafeFromDemon
from lib.logic.tools import (
    if_functioning,
    morning_delete,
    generic_ongoing_effect,
    select_target,
)


class Monk(Townsfolk):
    """The Monk."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Monk"

    @if_functioning(True)
    async def morning(self, ctx, enabled=True, epithet_string=""):
        """Apply the Monk's protection to a chosen target."""
        target = await select_target(
            ctx, f"Who did {self.parent.formatted_epithet(epithet_string)}, protect?"
        )
        if target:
            effect = _MonkProtection(ctx, target, self.parent)
            if not enabled:
                effect.disable(ctx)
            target.effects.append(effect)
        return [], []


@morning_delete()
@generic_ongoing_effect
class _MonkProtection(SafeFromDemon):
    """The Monk's protection."""

    pass
