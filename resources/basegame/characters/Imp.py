"""Contains the Imp class."""
from typing import Tuple, List

from lib.logic.Character import Demon
from lib.logic.Effect import Dead
from lib.logic.Player import Player
from lib.logic.tools import if_functioning, select_target
from lib.typings.context import Context
from lib.utils import safe_send


class Imp(Demon):
    """The Imp."""

    name: str = "Imp"
    playtest: bool = False

    @if_functioning(False)
    async def morning(self, ctx: Context) -> Tuple[List["Player"], List[str]]:
        """Apply the Imp's kill."""
        target = await select_target(ctx, f"Who did {self.parent.epithet}, kill?")
        if not target or target.is_status(ctx, "safe_from_demon") or target.ghost(ctx):
            return [], []

        target.add_effect(ctx, Dead, self.parent)

        # starpass
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
