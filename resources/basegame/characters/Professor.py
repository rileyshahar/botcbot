"""Contains the Professor class."""
from typing import Tuple, List

from discord.ext import commands

from lib.logic.Character import Townsfolk
from lib.logic.Effect import UsedAbility
from lib.logic.Player import Player
from lib.logic.tools import if_functioning, onetime_use, select_target
from lib.typings.context import Context


def _condition(player: Player, ctx: Context) -> bool:
    """Determine whether player registers as dead."""
    if player.ghost(ctx, registers=True):
        return True
    raise commands.BadArgument(f"{player.nick} is not dead.")


class Professor(Townsfolk):
    """The Professor."""

    name: str = "Professor"
    playtest: bool = False

    @if_functioning(True)
    @onetime_use
    async def morning(
        self, ctx: Context, enabled: bool = True, epithet_string: str = ""
    ) -> Tuple[List[Player], List[str]]:
        """Ask if the professor targeted anyone, then revive them if applicable."""
        target = await select_target(
            ctx,
            (
                f"Who did {self.parent.formatted_epithet(epithet_string)}, revive? "
                f'Or, say a variant of "no-one".'
            ),
            condition=_condition,
        )
        if target:
            self.parent.add_effect(ctx, UsedAbility, self.parent)
            if enabled and target.is_status(ctx, "townsfolk", registers=True):
                return [], [await target.revive(ctx)]
        return [], []
