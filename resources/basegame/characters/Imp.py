"""Contains the Imp class."""

from lib.logic.Character import Demon
from lib.logic.Effect import Dead
from lib.logic.tools import if_functioning, select_target
from lib.utils import safe_send


class Imp(Demon):
    """The Imp."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Imp"

    @if_functioning(False)
    async def morning(self, ctx):
        """Apply the Imp's kill."""
        target = await select_target(ctx, f"Who did {self.parent.epithet}, kill?")
        if target:
            if not target.is_status(ctx, "safe_from_demon") and not target.ghost(ctx):
                target.effects.append(Dead(ctx, target, self.parent))

                if target == self.parent:
                    while True:
                        chosen_minion = await select_target(
                            ctx, f"Which minion is the new Imp?"
                        )
                        if chosen_minion is None:
                            break
                        if chosen_minion.is_status(ctx, "minion", registers=True):
                            await chosen_minion.change_character(ctx, Imp)
                            break
                        await safe_send(ctx, "You must choose a minion.")

                return [target], []
        return [], []
