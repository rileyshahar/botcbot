"""Contains the Events cog, for handling listeners."""

import asyncio

from discord import HTTPException
from discord.ext import commands

from lib.bot import BOTCBot
from lib.logic.Character import Storyteller
from lib.logic.Player import Player
from lib.typings.context import Context
from lib.utils import get_player, safe_send, safe_bug_report

_report_bug_message = " Please report this bug to nihilistkitten#6937 or an admin."


async def _http_error_handler(ctx: Context, error: HTTPException):
    """Handle HTTP errors."""
    if error.code == 50006:
        # empty message
        await safe_send(
            ctx, "Uh oh! Unable to send an empty message." + _report_bug_message,
        )
        if safe_bug_report(ctx):
            await safe_send(ctx, f"```{error}```")
        raise error

    if error.code == 50035:
        # invalid body
        await safe_send(
            ctx,
            (
                "Uh oh! The response had an invalid body, likely due to length."
                + _report_bug_message
            ),
        )
        if safe_bug_report(ctx):
            await safe_send(ctx, f"```{error}```")
        raise error

    if error.code == 30003:
        # pin limit
        await safe_send(ctx, "Uh oh! The pin limit has been reached.")
        raise error


def _update_player_members(bot, after):
    """Update player members when they change."""
    try:
        player = get_player(bot.game, after)
        player.member = after
    except TypeError as e:
        if str(e) != "no current game":
            raise
    except ValueError as e:
        if str(e) != "player not found":
            raise


def _update_storyteller_list(bot, after, before):
    """Add new storytellers to the Storyteller list."""
    if bot.storyteller_role not in before.roles and bot.storyteller_role in after.roles:
        bot.game.storytellers.append(Player(after, Storyteller, None))
    bot.backup()


class Events(commands.Cog):
    """Listeners for event handling."""

    def __init__(self, bot: BOTCBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Run immediately after startup."""
        print("Logged in as", self.bot.user.name)
        print("ID:", self.bot.user.id)
        print("Server:", self.bot.server)
        print("Gameplay Channel: #", self.bot.channel.name)

        # restore backups
        await self.bot.restore_backup()

        # update status
        await self.bot.update_status()

        print("------")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context, error: Exception):
        """Handle command errors."""

        # Ignore commands with local handling
        if hasattr(ctx.command, "on_error"):
            return

        # Check original exceptions for commands.CommandInvokeError
        error = getattr(error, "original", error)

        if isinstance(error, commands.CheckFailure):
            # commands which fail contextual checks

            if isinstance(error, commands.NotOwner):
                # commands.is_owner()
                return await safe_send(
                    ctx, "Stop trying to play around with debug tools, please! ;)"
                )

            if str(error):
                # most checks
                return await safe_send(ctx, str(error))

            # checks.is_dm() and checks.is_in_channel()
            return

        if isinstance(error, ValueError):
            # value errors

            if str(error) == "cancelled":
                # raised by lib.utils.get_input if input is cancel
                await safe_send(ctx, "Cancelled!")
                return

            if str(error) == "command called":
                # raised by lib.utils.get_input if another command is called
                return

            if str(error) == "player not found":
                # raised by lib.utils.get_player
                raise error

            if str(error) == "unmatched seating order length":
                # raised by lib.logic.Game.Game.reseat
                await safe_send(
                    ctx, "The new and old seating orders have differing lengths."
                )
                return

        elif isinstance(error, HTTPException):
            # errors in HTTP request operations
            await _http_error_handler(ctx, error)

        elif isinstance(error, SyntaxError):
            # syntax errors
            await safe_send(
                ctx, "Uh oh! There's a syntax error somewhere." + _report_bug_message,
            )
            if safe_bug_report(ctx):
                await safe_send(ctx, f"```{error}```")
            raise error

        elif isinstance(error, asyncio.TimeoutError):
            # timeout error
            return await safe_send(ctx, "Timed out.")

        elif isinstance(error, commands.CommandNotFound):
            # unknown commands
            if ctx.guild is None:
                return await safe_send(
                    ctx,
                    (
                        f"Command not found: {ctx.invoked_with}. "
                        f"For a list of commands, try `{ctx.prefix}help`."
                    ),
                )
            return

        elif isinstance(error, commands.errors.MissingRequiredArgument):
            # not enough arguments
            await safe_send(
                ctx, "Uh oh! You're missing arguments. Hopefully this helps:"
            )
            return await ctx.send_help(ctx.command)

        elif isinstance(error, commands.BadArgument):
            # converter error
            return await safe_send(ctx, str(error))

        elif isinstance(error, commands.DisabledCommand):
            # disabled command
            return await safe_send(ctx, f"{ctx.command.name} has been disabled.")

        await safe_send(
            ctx, "Uh oh! An unknown error occured." + _report_bug_message,
        )
        if safe_bug_report(ctx):
            await safe_send(ctx, f"```{error}```")
        raise error

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Handle member updates."""
        if self.bot.game:

            # update player objects with changes
            _update_player_members(self.bot, after)

            # add new storytellers to the seating order
            _update_storyteller_list(self.bot, after, before)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle messages."""
        if message.author.bot:
            return

        if not message.channel == self.bot.channel:
            return

        if self.bot.game is None or self.bot.game.current_day is None:
            return

        try:
            player = get_player(self.bot.game, message.author.id, False)
            await player.make_active(self.bot.game)
        except TypeError as e:
            if str(e) != "no current game":
                raise
        except ValueError as e:
            if str(e) != "player not found":
                raise


def setup(bot: BOTCBot):
    """Set the cog up."""
    bot.add_cog(Events(bot))
