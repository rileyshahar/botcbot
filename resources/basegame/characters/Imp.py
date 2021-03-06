"""Contains the Imp class."""
from typing import TYPE_CHECKING, List, Tuple

from lib.logic.Character import Demon
from lib.logic.charcreation import (MorningTargetCallMixin, if_functioning,
                                    kill_selector, select_target)
from lib.logic.Player import Player
from lib.utils import safe_send

if TYPE_CHECKING:
    from lib.typings.context import GameContext


class Imp(Demon, MorningTargetCallMixin):
    """The Imp."""

    name: str = "Imp"
    playtest: bool = False

    @if_functioning(False)
    async def morning(self, ctx: "GameContext") -> Tuple[List[Player], List[str]]:
        """Apply the Imp's kill."""
        out = await kill_selector(self, ctx)
        target = out[0][0]

        # starpass
        if target == self.parent:
            while True:
                chosen_minion = await select_target(
                    ctx, f"Which minion is the new Imp?"
                )
                if chosen_minion is None:
                    break
                if chosen_minion.is_status(ctx.bot.game, "minion", registers=True):
                    await chosen_minion.change_character(ctx, Imp)
                    break
                await safe_send(ctx, "You must choose a minion.")

        return out
