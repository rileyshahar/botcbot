"""Contains the Poisoner class."""

from lib.logic.Character import Minion
from lib.logic.Effect import Poisoned
from lib.logic.tools import (
    if_functioning,
    evening_delete,
    generic_ongoing_effect,
    select_target,
)


class Poisoner(Minion):
    """The Poisoner."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Poisoner"

    @if_functioning(True)
    async def morning(self, ctx, enabled=True, epithet_string=""):
        """Apply the Poisoner's poison to a chosen target."""
        target = await select_target(
            ctx, f"Who did {self.parent.formatted_epithet(epithet_string)}, poison?"
        )
        if target:
            effect = _PoisonerPoison(ctx, target, self.parent)
            if not enabled:
                effect.disable(ctx)
            target.effects.append(effect)
        return [], []


@evening_delete()
@generic_ongoing_effect
class _PoisonerPoison(Poisoned):
    """The Poisoner's poison."""

    pass
