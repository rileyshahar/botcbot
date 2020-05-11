"""Contains the GameProgression cog, for commands related to game progression."""

from os.path import isfile
from typing import List

from discord.ext import commands

from lib import checks
from lib.logic.Effect import Dead
from lib.logic.Player import Player
from lib.logic.converters import to_script
from lib.logic.playerconverter import to_player
from lib.typings.context import Context
from lib.utils import safe_send, get_bool_input


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
        await safe_send(ctx, "Started the game successfully.")

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
            # TODO: unpin the script messages as well
            for msg in await ctx.bot.channel.pins():
                if msg.created_at >= ctx.bot.game.seating_order_message.created_at:
                    await msg.unpin()

            # backup
            i = 1
            while isfile(f"{ctx.bot.bot_name}/old/game_{i}.pckl"):
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

    @commands.group()
    @checks.is_night()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def startday(self, ctx):
        """Start the day.

        This will perform the action of most characters in the night order.
        It does not handle info roles or other roles with no effect on the gamestate.
        """
        return await ctx.bot.game.startday(ctx)

    @startday.command()
    async def arbitrarykills(self, ctx: Context, *, kills: str):
        """Start the day with arbitrary additional kills at the beginning of the night.

        kills: Any players to kill.
        This goes through protection, but cannot kill dead players.
        The players are killed at the beginning of the night.
        """
        kills_actual = []  # type: List[Player]
        # convert kills
        for kill_string in kills:
            kills_actual.append(await to_player(ctx, kill_string))

        for player in kills_actual:
            if not player.ghost(ctx):
                player.add_effect(ctx, Dead, player)

        await ctx.bot.game.startday(ctx, kills_actual)

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


def setup(bot):
    """Set the cog up."""
    bot.add_cog(GameProgression(bot))
