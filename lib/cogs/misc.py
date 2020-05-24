"""Contains the Misc cog, for miscellaneous commands."""
from discord.ext import commands

from lib import checks
from lib.typings.context import Context
from lib.utils import safe_send


class Misc(commands.Cog):
    """Miscellaneous commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.is_dm()
    async def playercommands(self, ctx: Context):
        """View all player commands."""
        message_text = "```"
        command_list = [
            command.name
            for command in ctx.bot.commands
            if command.cog is not None
            and command.cog.qualified_name
            not in ("Effects", "Game Management", "Info", "Game Progression")
            and not command.hidden
        ]
        command_list.sort()
        for command in command_list:
            message_text += f"\n{command}"
        message_text += (
            f"\n\nType {ctx.prefix}help command for more info on a command.```"
        )
        await safe_send(ctx, message_text)

    @commands.command()
    @checks.is_dm()
    async def clear(self, ctx: Context):
        """Send whitespace to clear past messages."""
        whitespace = "\u200B\n" * 25
        await safe_send(ctx, whitespace + "Clearing!" + whitespace)


def setup(bot):
    """Set the cog up."""
    bot.add_cog(Misc(bot))
