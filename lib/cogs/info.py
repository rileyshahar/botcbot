"""Contains the Info cog, for commands related to viewing game info."""
import discord
from discord.ext import commands

from lib import checks
from lib.bot import BOTCBot
from lib.logic.playerconverter import to_player
from lib.logic.tools import generate_message_tally
from lib.typings.context import Context
from lib.utils import safe_send


class Info(commands.Cog, name="Info"):
    """Commands for viewing game information."""

    @commands.command()
    @checks.is_day()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def notactive(self, ctx):
        """List the players yet to speak today."""
        not_active = ctx.bot.game.not_active

        if not not_active:
            message_text = "Everyone has spoken!"

        else:
            message_text = "The following players have not spoken today:"

            for player in ctx.bot.game.not_active:
                message_text += f"\n{player.nick}"

        await safe_send(ctx, message_text)

    @commands.command()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def messagetally(self, ctx, idn: int):
        """Generate a message tally.

        idn: The ID of the message to tally messages since.
        To get the id, right-click on the message in discord developer mode.
        The message must be in the main gameplay channel.
        """
        try:
            time = (await ctx.bot.channel.fetch_message(idn)).created_at
            await safe_send(
                ctx, generate_message_tally(ctx, lambda msg: msg["time"] >= time,),
            )
        except discord.errors.NotFound:
            await safe_send(ctx, f"Message with ID {idn} not found.")

    @commands.command()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def grimoire(self, ctx: Context):
        """Generate the grimoire."""

        message_text = "**Grimoire:**"

        for player in ctx.bot.game.seating_order:
            message_text += f"\n{player.epithet}"
            effect_list = [
                effect
                for effect in player.effects
                if effect.appears and not effect.disabled
            ]
            if effect_list:
                message_text += ":"
                for effect in effect_list:
                    message_text += f"\n> {effect.name}"

        await safe_send(ctx, message_text)

    @commands.command()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def sthistory(self, ctx, player1: str, player2: str):
        """View the message history between two players."""
        player1_actual = await to_player(ctx, player1)
        player2_actual = await to_player(ctx, player2)

        await safe_send(ctx, player1_actual.message_history_with(player2_actual))


def setup(bot: BOTCBot):
    """Set the cog up."""
    bot.add_cog(Info(bot))
