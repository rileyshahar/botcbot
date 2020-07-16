"""Contains the Debug cog for commands related to debugging."""

from typing import List

from discord.ext import commands

from lib import checks
from lib.bot import BOTCBot
from lib.logic.Effect import status_list
from lib.typings.context import Context, GameContext
from lib.utils import aexec, list_to_plural_string, safe_send


class Debug(commands.Cog, command_attrs=dict(hidden=True)):  # type: ignore
    """Commands for debugging code."""

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.command(name="unpinall")
    @commands.is_owner()
    @checks.is_dm()
    async def _unpinall(self, ctx: Context):
        """Unpin all messages in channel."""
        with ctx.typing():
            for msg in await ctx.bot.channel.pins():
                await msg.unpin()

        await safe_send(ctx, "Unpinned all messages.")

    @commands.command(name="eval")
    @commands.is_owner()
    @checks.is_dm()
    async def _eval(self, ctx: Context, *, code: str):
        """Execute code, sending its output to ctx."""
        await safe_send(ctx, await aexec("return " + code, ctx))

    @commands.command(name="exec")
    @commands.is_owner()
    @checks.is_dm()
    async def _exec(self, ctx: Context, *, code: str):
        """Execute code."""
        await aexec(code, ctx)

    @commands.command(name="load")
    @commands.is_owner()
    @checks.is_dm()
    async def _load(self, ctx: Context, *, cog: str):
        """Load cog."""
        try:
            self.bot.load_extension(cog)
            await safe_send(ctx, "Load successful.")
        except commands.errors.ExtensionNotFound:
            try:
                self.bot.load_extension("lib.cogs." + cog)
                await safe_send(ctx, "Load successful.")
            except commands.errors.ExtensionNotFound:
                await safe_send(ctx, f"Extension not found: {cog}.")

    @commands.command(name="reload")
    @commands.is_owner()
    @checks.is_dm()
    async def _reload(self, ctx: Context, *, cog: str):
        """Reload cog."""
        try:
            self.bot.reload_extension(cog)
            await safe_send(ctx, "Reload successful.")
        except commands.errors.ExtensionNotLoaded:
            try:
                self.bot.reload_extension("lib.cogs." + cog)
                await safe_send(ctx, "Reload successful.")
            except commands.errors.ExtensionNotLoaded:
                await safe_send(ctx, f"Extension not loaded: {cog}.")

    @commands.command(name="unload")
    @commands.is_owner()
    @checks.is_dm()
    async def _unload(self, ctx: Context, *, cog: str):
        """Unload cog."""
        try:
            self.bot.unload_extension(cog)
            await safe_send(ctx, "Unload successful.")
        except commands.errors.ExtensionNotLoaded:
            try:
                self.bot.unload_extension("lib.cogs." + cog)
                await safe_send(ctx, "Unload successful.")
            except commands.errors.ExtensionNotLoaded:
                await safe_send(ctx, f"Extension not loaded: {cog}.")

    @commands.command(name="detailedgrimoire")
    @commands.is_owner()
    @checks.is_game()
    @checks.is_dm()
    async def _detailedgrimoire(self, ctx: GameContext):
        """Display a detailed text grimoire."""
        message_text = "**Grimoire:**"
        for player in ctx.bot.game.seating_order:
            message_text += f"\n\n__{player.epithet}:__"
            for effect in player.effects:
                message_text += f"\n{effect.name}:"
                message_text += f"\n> Source: {effect.source_player.epithet}"
                message_text += f"\n> Disabled: {effect.disabled}"
                statuses = []  # type: List[str]
                registers_statuses = []  # type: List[str]
                for status in status_list:
                    if effect.status(ctx.bot.game, status):
                        statuses.append(status)
                    if effect.registers_status(ctx.bot.game, status):
                        registers_statuses.append(status)
                message_text += "\n> Causes: "
                message_text += list_to_plural_string(statuses, "none")[0]
                message_text += "\n> Causes registering: "
                message_text += list_to_plural_string(registers_statuses, "none")[0]

        await safe_send(ctx, message_text)


def setup(bot: BOTCBot):
    """Set the cog up."""
    bot.add_cog(Debug(bot))
