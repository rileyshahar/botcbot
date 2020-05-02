"""Contains the EffectManagement cog for commands relating to the gamestate."""

from typing import Type

from discord.ext import commands

from lib import checks
from lib.bot import BOTCBot
from lib.logic import Effect
from lib.logic.Player import Player
from lib.logic.playerconverter import to_player
from lib.logic.tools import generic_ongoing_effect

from lib.typings.context import Context
from lib.utils import safe_send


class EffectManagement(commands.Cog, name="[ST] Effects"):
    """Tools for effect management."""

    def __init__(self, bot: BOTCBot):
        self.bot = bot

    @commands.group()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def registers(self, ctx: Context):
        """Change what a player registers as.

        Primarily used for Recluse, Spy, etc.
        """
        if ctx.invoked_subcommand is None:
            await safe_send(ctx, "Invalid registers command. Hopefully this helps:")
            return await ctx.send_help(ctx.bot.get_command("registers"))

    @registers.command()
    async def good(self, ctx: Context, player: str):
        """Make a player register as good."""
        player_actual = await to_player(ctx, player)
        await _effect_adder(ctx, player_actual, Effect.RegistersGood)

    @registers.command()
    async def evil(self, ctx: Context, player: str):
        """Make a player register as evil."""
        player_actual = await to_player(ctx, player)
        await _effect_adder(ctx, player_actual, Effect.RegistersEvil)

    @registers.command()
    async def townsfolk(self, ctx: Context, player: str):
        """Make a player register as a Townsfolk."""
        player_actual = await to_player(ctx, player)
        await _effect_adder(ctx, player_actual, Effect.RegistersTownsfolk)

    @registers.command()
    async def outsider(self, ctx: Context, player: str):
        """Make a player register as an Outsider."""
        player_actual = await to_player(ctx, player)
        await _effect_adder(ctx, player_actual, Effect.RegistersOutsider)

    @registers.command()
    async def minion(self, ctx: Context, player: str):
        """Make a player register as a Minion."""
        player_actual = await to_player(ctx, player)
        await _effect_adder(ctx, player_actual, Effect.RegistersMinion)

    @registers.command()
    async def demon(self, ctx: Context, player: str):
        """Make a player register as a Demon."""
        player_actual = await to_player(ctx, player)
        await _effect_adder(ctx, player_actual, Effect.RegistersDemon)

    # noinspection PyArgumentList
    # this seems like a false positive
    @registers.command()
    async def clear(self, ctx: Context, player: str):
        """Clear all ST-added registration effects on a player."""
        player_actual = await to_player(ctx, player)
        effect_list = [x for x in player_actual.effects]
        i = 0
        for effect in effect_list:
            if issubclass(
                effect,
                (
                    Effect.RegistersGood,
                    Effect.RegistersEvil,
                    Effect.RegistersTownsfolk,
                    Effect.RegistersOutsider,
                    Effect.RegistersMinion,
                    Effect.RegistersDemon,
                ),
            ):
                effect.delete(ctx)
                i += 1
        if i == 0:
            await safe_send(ctx, f"{player_actual.nick} is not registering unusually.")
        else:
            plural = "s" if i > 1 else ""
            await safe_send(
                ctx,
                f"Successfully removed {i} effect{plural} from {player_actual.nick}.",
            )

    @commands.command()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def poison(
        self, ctx: Context, player: str, source: str = None,
    ):
        """Poison a player.

        The source may be any player. If empty, the effect will have no source.
        """
        # TODO: figure out what the source should look like here

        player_actual = await to_player(ctx, player)
        if source is not None:
            source_actual = await to_player(ctx, source, includes_storytellers=True)
        else:
            source_actual = ctx.bot.game.storytellers[0]
        await _effect_adder(
            ctx, player_actual, generic_ongoing_effect(Effect.Poisoned), source_actual
        )


def setup(bot: BOTCBot):
    """Set the cog up."""
    bot.add_cog(EffectManagement(bot))


async def _effect_adder(
    ctx: Context, player: Player, effect: Type[Effect.Effect], source: Player = None
):
    """Add effect to player."""
    source = source or player
    effect_object = player.add_effect(ctx, effect, source)
    if source == player or source.character_type(ctx) == "storyteller":
        source_text = ""
    else:
        source_text = f"with source {source.nick} "
    await safe_send(
        ctx,
        f"Successfully added effect {effect_object.name} {source_text}to {player.nick}.",
    )
