"""Contains the Playing cog, for commands related to gameplay."""

from typing import Optional

from discord.ext import commands

from lib import checks
from lib.exceptions import AlreadyNomniatedError
from lib.logic.Player import Player
from lib.logic.playerconverter import to_player
from lib.typings.context import DayContext, GameContext, VoteContext
from lib.utils import get_player, safe_send, to_bool


class Playing(commands.Cog):
    """Commands for playing the game."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.is_not_vote()
    @checks.noms_open()
    @checks.is_day()
    @checks.is_player()
    @checks.is_game()
    async def nominate(self, ctx: "DayContext", *, nominee: str):
        """Nominate a player for execution.

        nominee: The player to be nominated, or "the storytellers".
        """
        try:
            await ctx.bot.game.current_day.nominate(
                ctx, nominee, get_player(ctx.bot.game, ctx.message.author.id)
            )

        # if they can't nominate
        # raised by current_day.nominate
        except AlreadyNomniatedError:
            return await safe_send(ctx, "You cannot nominate today.")

    @commands.command()
    @checks.is_vote()
    @checks.is_day()
    @checks.is_player()
    @checks.is_game()
    async def vote(self, ctx: "VoteContext", *, vote: str):
        """Vote in an ongoing nomination.

        vote: The vote to submit.
        """
        vote_actual = to_bool(vote, "vote")

        player = get_player(ctx.bot.game, ctx.message.author.id)

        # verify it's their turn to vote
        if ctx.bot.game.current_day.current_vote.to_vote != player:
            await safe_send(
                ctx,
                (
                    "It is {actual_voter}'s vote, not yours, silly! "
                    "(Unless this is a bug. In which case I'm silly. "
                    "I hope I'm not silly.)"
                ).format(
                    actual_voter=ctx.bot.game.current_day.current_vote.to_vote.nick
                ),
            )

        # do the vote
        await ctx.bot.game.current_day.current_vote.vote(ctx, player, vote_actual)

    @commands.command(aliases=["message"])
    @checks.pms_open()
    @checks.is_day()
    @checks.is_player()
    @checks.is_game()
    @checks.is_dm()
    async def pm(self, ctx: "DayContext", *, recipient: str = None):
        """Message a player or storyteller.

        recipient: The player or storyteller to recieve the message.
        If none, this will list all possible recipients.

        You will be asked about the content of the message.
        You can cancel by saying "cancel".
        """
        recipient = recipient or ""
        recipient_actual = await to_player(ctx, recipient, includes_storytellers=True)

        await recipient_actual.message(
            ctx, get_player(ctx.bot.game, ctx.message.author.id)
        )

    @commands.command()
    @checks.pms_open()
    @checks.is_day()
    @checks.is_player()
    @checks.is_game()
    @checks.is_dm()
    async def reply(self, ctx: "DayContext"):
        """Reply to the previously recieved message.

        You will be asked about the content of the message.
        You can cancel by saying "cancel".
        """
        author_player = get_player(ctx.bot.game, ctx.message.author.id)

        most_recent_time = ctx.bot.game.seating_order_message.created_at
        most_recent_author = None  # type: Optional[Player]

        for message in author_player.message_history:
            if message["from"] != author_player:
                if message["time"] > most_recent_time:
                    most_recent_time = message["time"]
                    most_recent_author = message["from"]

        if not most_recent_author:
            await safe_send(ctx, "No messages to reply to.")

        else:
            await most_recent_author.message(ctx, author_player)

    @commands.command()
    @checks.is_vote()
    @checks.is_day()
    @checks.is_player()
    @checks.is_game()
    @checks.is_dm()
    async def prevote(self, ctx: "VoteContext", vote: str):
        """Prevote in an ongoing nomination.

        vote: The prevote to queue.

        When it's your turn to vote, this will automatically submit the queued vote.
        """
        actual_vt = int(to_bool(vote, "vote"))
        await ctx.bot.game.current_day.current_vote.prevote(
            ctx, get_player(ctx.bot.game, ctx.author.id), actual_vt
        )

    @commands.command()
    @checks.is_player()
    @checks.is_game()
    @checks.is_dm()
    async def history(self, ctx: "GameContext", *, player: str = None):
        """View your message history.

        player: The player to view your message history with.
        If none, this will list all possible players.
        """
        player = player or ""
        player_actual = await to_player(ctx, player)
        await safe_send(
            ctx,
            get_player(ctx.bot.game, ctx.author.id, False).message_history_with(
                player_actual
            ),
        )

    @commands.command()
    @checks.is_day()
    @checks.is_player()
    @checks.is_game()
    @checks.is_dm()
    async def skip(self, ctx: "DayContext"):
        """Skip your right to nominate for the current day.

        You will still be able to nominate.
        However, if all players nominate or skip, the storytellers may end the day.
        """
        author_player = get_player(ctx.bot.game, ctx.author.id, False)
        if author_player.can_nominate(ctx.bot.game):
            await author_player.add_nomination(ctx, skip=True)
            await safe_send(ctx.bot.channel, f"{author_player.nick} has skipped.")
        else:
            raise commands.BadArgument("You cannot nominate today.")


def setup(bot):
    """Set the cog up."""
    bot.add_cog(Playing(bot))
