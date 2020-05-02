"""Contains the Info cog, for commands related to viewing game info."""

from discord.ext import commands

from lib import checks
from lib.bot import BOTCBot
from lib.utils import safe_send


class Info(commands.Cog, name="[ST] Info"):
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


def setup(bot: BOTCBot):
    """Set the cog up."""
    bot.add_cog(Info(bot))
