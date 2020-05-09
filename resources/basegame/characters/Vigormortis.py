"""Contains the Vigormortis class."""
from typing import List, Tuple

from discord.ext import commands

from lib.logic.Character import Demon
from lib.logic.Effect import Dead, Poisoned
from lib.logic.Player import Player
from lib.logic.tools import if_functioning, select_target, generic_ongoing_effect
from lib.typings.context import Context


class _VigormortisDead(Dead):
    """The Vigormortis's kill."""

    # TODO: instead of checking if the vig is functioning spawn a new effect
    # as part of the behavior of source_drunkpoisoned_cleanup and source_death_cleanup
    # which stops affected_player from functioning
    # checking if the vig is functioning probably causes recursion errors somewhere
    # ex if the vig kills a poisoner and then the poisoner targets a vig
    # although this is an unresolved issue in the game's rules as well

    def not_functioning(self, ctx: Context):
        """Allow minions to function while killed by Vigormortis."""
        if self.affected_player.is_status(
            ctx, "minion", registers=True
        ) and self.source_player.functioning(ctx):
            return False
        return True


def _condition(player: Player, ctx: Context, **kwargs) -> bool:
    """Determine whether player registers as a townsfolk."""
    target = kwargs.pop("target")
    if player in target.neighbors(
        ctx, lambda x, y: x.is_status(y, "townsfolk", registers=True)
    ):
        return True
    raise commands.BadArgument(
        f"{player.nick} is not a Townsfolk neighbor of {target.nick}."
    )


class Vigormortis(Demon):
    """The Vigormortis."""

    name: str = "Vigormortis"
    playtest: bool = False

    @if_functioning(False)
    async def morning(self, ctx: Context) -> Tuple[List[Player], List[str]]:
        """Apply the Vigormortis's kill to a chosen target.

        If a Minion is chosen, apply the corresponding poison.
        """
        target = await select_target(ctx, f"Who did {self.parent.epithet}, kill?")
        if not target or target.is_status(ctx, "safe_from_demon") or target.ghost(ctx):
            return [], []

        target.add_effect(ctx, _VigormortisDead, self.parent)

        # vigormortis poison
        if target.is_status(ctx, "minion", registers=True):

            new_target = await select_target(
                ctx, "Who did that poison?", condition=_condition, target=target,
            )
            if new_target:
                new_target.add_effect(
                    ctx, generic_ongoing_effect(Poisoned), self.parent
                )
                # TODO: this needs to be a custom Poisoned subclass that has nice
                # cleanup functions for if the minion changes character
        return [target], []
