"""Contains the GameProgression cog, for commands related to game progression."""
from datetime import datetime, timedelta
from os.path import isfile

import pytz
from discord.ext import commands

from lib import checks
from lib.logic.converters import to_script
from lib.typings.context import Context
from lib.utils import safe_send, get_bool_input


def _is_dst():
    """Check if it's currently daylight savings time in the US."""
    x = datetime(datetime.now().year, 1, 1, 0, 0, 0, tzinfo=pytz.timezone("US/Eastern"))
    y = datetime.now(pytz.timezone("US/Eastern"))
    return y.utcoffset() != x.utcoffset()


class GameProgression(commands.Cog, name="Game Progression"):
    """Commands for game progression."""

    @commands.command()
    @checks.is_not_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def startgame(self, ctx: Context, *, script: str):
        """Start the game.

        script: The game's script. Available scripts can be viewed with `script list`.

        You'll be asked for two pieces of input:

        First, the seating order:
        This is a line-separated, ordered list of the game's players.
        Do not include travelers.

        Second, the characters:
        This is a line-separated, ordered list of the corresponding characters.
        """
        await ctx.bot.start_game(ctx, to_script(ctx, script))

    @commands.command()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def endgame(self, ctx: Context, winner: str):
        """End the game.

        winner: 'good' or 'evil'. Can be 'neutral' in the event of a rerack.

        This command often takes a long time, as it unpins a large number of messages.
        """
        with ctx.typing():

            # verify valid winner
            winner = winner.lower()
            if winner not in ["good", "evil", "neutral"]:
                raise commands.BadArgument(
                    "The winner must be 'good,' 'evil,' or 'neutral,' exactly."
                )

            # set winner
            ctx.bot.game.winner = winner

            # endgame message
            if winner != "neutral":
                await safe_send(
                    ctx.bot.channel,
                    f"{ctx.bot.player_role.mention}, {winner} has won. Good game!",
                )
            else:
                await safe_send(
                    ctx.bot.channel,
                    f"{ctx.bot.player_role.mention}, the game is being remade.",
                )

            # unpin messages
            for msg in await ctx.bot.channel.pins():
                if (
                    msg.created_at
                    >= ctx.bot.game.seating_order_message.created_at
                    - timedelta(minutes=1)  # this will unpin the script messages too
                ):
                    await msg.unpin()

            # backup
            i = 1
            while isfile(f"resources/backup/{ctx.bot.bot_name}/old/game_{i}.pckl"):
                i += 1
            ctx.bot.backup(f"old/game_{i}.pckl")

            # thank storytellers
            for st in ctx.bot.game.storytellers:
                await safe_send(
                    st.member, "Thank you for storytelling! We appreciate you <3"
                )

            # delete game
            ctx.bot.game = None

            # complete
            await safe_send(ctx, "Ended the game successfully.")
            return

    @commands.command()
    @checks.is_day()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def endday(self, ctx: Context):
        """End the current day."""
        # confirm
        if not await get_bool_input(
            ctx,
            (
                "This will end the day without executing. "
                "To end the day via execution, use the `execute` command. "
                "Do you want to continue?"
            ),
        ):
            await safe_send(ctx, "Cancelled.")
            return

        await safe_send(ctx.bot.channel, "No one was executed.")
        await ctx.bot.game.current_day.end(ctx)

    @commands.command()
    @checks.is_night()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def currentstep(self, ctx: Context):
        """View the current step in the current night."""
        await ctx.bot.game.current_night.current_step(ctx)

    @commands.command()
    @checks.is_night()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def nextstep(self, ctx):
        """Progress the current night."""
        await ctx.bot.game.current_night.next_step(ctx)

    @commands.group(name="open")
    @checks.is_day()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def _open(self, ctx: Context):
        """Open PMs and nominations.

        The bot automatically opens nominations and PMs at the end of a nomination.
        Therefore, this should generally only be used for troubleshooting.
        """
        if ctx.invoked_subcommand is None:
            await ctx.bot.game.current_day.open_pms(ctx)
            await ctx.bot.game.current_day.open_noms(ctx)

    @_open.command()
    @checks.is_day()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def noms(self, ctx: Context):
        """Open nominations."""
        await ctx.bot.game.current_day.open_noms(ctx)

    @_open.command()
    @checks.is_day()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def pms(self, ctx: Context):
        """Open PMs."""
        await ctx.bot.game.current_day.open_pms(ctx)

    @commands.group(name="close")
    @checks.is_day()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def _close(self, ctx: Context):
        """Close PMs and nominations.

        The bot automatically closes nominations and PMs at the start of a nomination.
        Therefore, this should generally only be used for troubleshooting.
        """
        if ctx.invoked_subcommand is None:
            await ctx.bot.game.current_day.close_pms(ctx)
            await ctx.bot.game.current_day.close_noms(ctx)

    @_close.command(name="noms")
    @checks.is_day()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def _noms(self, ctx: Context):
        """Close nominations."""
        await ctx.bot.game.current_day.close_noms(ctx)

    @_close.command()
    @checks.is_day()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def _pms(self, ctx: Context):
        """Close PMs."""
        await ctx.bot.game.current_day.close_pms(ctx)

    @commands.command()
    @checks.is_day()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def setdeadline(self, ctx: Context, length: int):
        """Set a deadline for the current day and open nominations.

        length: The number of hours for the deadline to last.
        The deadline will be rounded up to the nearest hour or half-hour.
        """
        now = datetime.now()
        time_adder = now + timedelta(hours=length)
        time = time_adder + (datetime.min - time_adder) % timedelta(minutes=30)
        utc = time.astimezone(pytz.utc).strftime("%H:%M")
        pacific = time.astimezone(pytz.timezone("US/Pacific")).strftime("%-I:%M %p")
        eastern = time.astimezone(pytz.timezone("US/Eastern")).strftime("%-I:%M %p")

        utc_name = "UTC"
        if _is_dst():
            pacific_name = "PDT"
            eastern_name = "EDT"
        else:
            pacific_name = "PST"
            eastern_name = "EST"

        announcement = await safe_send(
            ctx.bot.channel,
            (
                f"{ctx.bot.player_role.mention}, nominations are open! "
                f"The deadline is {pacific} {pacific_name} / {eastern} {eastern_name} "
                f"/ {utc} {utc_name} unless someone nominates or everyone skips."
            ),
        )
        await announcement.pin()
        await safe_send(ctx, f"Successfully set a deadline in {length} hours.")

        await ctx.bot.game.current_day.open_noms(ctx)


def setup(bot):
    """Set the cog up."""
    bot.add_cog(GameProgression(bot))
