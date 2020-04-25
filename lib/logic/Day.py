"""Contains the Day class."""

from typing import List, Optional, Tuple

from discord.ext import commands
from numpy import ceil

from lib.logic.Player import Player
from lib.logic.Vote import Vote
from lib.logic.playerconverter import to_player
from lib.typings.context import Context
from lib.utils import safe_send, safe_bug_report


class Day:
    """Stores information about a specific day.

    Attributes
    ----------
    is_pms : bool
        Whether PMs are open.
    is_noms : bool
        Whether nominations are open.
    past_votes : List[Vote]
        The day's previous votes.
    current_vote : Vote
        The day's current vote, or None.
    about_to_die : Tuple[Player, int, int]
        The player currently about to die, their vote tally, and the announcement ID.
    vote_end_messages : List[int]
        The IDs of messages announcing the end of votes.
    """

    def __init__(self):
        self.is_pms = True  # type: bool
        self.is_noms = False  # type: bool
        self.past_votes = []  # type: List[Vote]
        self.current_vote = None  # type: Optional[Vote]
        self.about_to_die = None  # type: Optional[Tuple[Player, int, int]]
        self.vote_end_messages = []  # type: List[int]

    async def nominate(self, ctx: Context, nominee_str: str, nominator: Player):
        """Begin a vote on the nominee.

        Parameters
        ----------
        ctx : Context
            The invocation context.
        nominee_str : str
            The user input to attempt to generate a nominee from.
        nominator : Player
            The player to be nominated.
        """
        # determine the nominee
        nominee = await _determine_nominee(ctx, nominee_str)

        # verify that the nominator can nominate
        _check_valid_nominator(ctx, nominator, nominee)

        # verify that the nominee can be nominated
        _check_valid_nominee(ctx, nominator, nominee)

        # check effects
        proceed = True
        for player in ctx.bot.game.seating_order:
            proceed = (
                await player.character.nomination(ctx, nominee, nominator) and proceed
            )
            effect_list = [x for x in player.effects]
            for effect in effect_list:
                proceed = await effect.nomination(ctx, nominee, nominator) and proceed

        if not proceed:
            return

        # adjust the nominator and nominee
        nominator.nominations_today += int(
            nominee.character_type(ctx) not in ["storyteller", "traveler"]
        )
        nominee.has_been_nominated = True

        # close pms and nominations
        await self.close_pms(ctx)
        await self.close_noms(ctx)

        # start the vote
        self.current_vote = Vote(ctx, nominee, nominator)

        # send announcement message
        message_text = generate_nomination_message_text(
            ctx,
            nominator,
            nominee,
            traveler=self.current_vote.traveler,
            proceed=True,
            majority=int(ceil(self.current_vote.majority)),
            about_to_die=self.about_to_die,
        )
        msg = await safe_send(ctx.bot.channel, message_text)

        # pin
        await msg.pin()
        self.current_vote.announcements.append(msg.id)

        # start voting!
        await self.current_vote.call_next(ctx)

    async def open_pms(self, ctx: Context):
        """Open PMs."""
        self.is_pms = True
        for st in ctx.bot.game.storytellers:
            await safe_send(st.member, "PMs are now open.")
        await ctx.bot.update_status()

    async def open_noms(self, ctx: Context):
        """Open nominations."""
        self.is_noms = True
        for st in ctx.bot.game.storytellers:
            await safe_send(st.member, "Nominations are now open.")
        await ctx.bot.update_status()

    async def close_pms(self, ctx: Context):
        """Close PMs."""
        self.is_pms = False
        for st in ctx.bot.game.storytellers:
            await safe_send(st.member, "PMs are now closed.")
        await ctx.bot.update_status()

    async def close_noms(self, ctx: Context):
        """Close nominations."""
        self.is_noms = False
        for st in ctx.bot.game.storytellers:
            await safe_send(st.member, "Nominations are now closed.")
        await ctx.bot.update_status()

    async def end(self, ctx: Context):
        """End the day."""
        # remove the day
        ctx.bot.game.past_days.append(self)
        ctx.bot.game.current_day = None

        # cleanup effects
        for player in ctx.bot.game.seating_order:
            effect_list = [x for x in player.effects]
            for effect in effect_list:
                effect.evening_cleanup(ctx)

        # remove the current vote
        if self.current_vote:
            await self.current_vote.cancel(ctx)

        # announcement
        await safe_send(
            ctx.bot.channel, f"{ctx.bot.player_role.mention}, go to sleep!",
        )

        # complete
        if safe_bug_report(ctx):
            await safe_send(ctx, "Successfully ended the day.")


def _check_valid_nominee(ctx: Context, nominator: Player, nominee: Player):
    """Check that the nominee is a valid nominee, else raise an exception."""
    if nominee.character_type(ctx) == "storyteller":  # atheist nominations
        for st in ctx.bot.game.storytellers:
            if not st.can_be_nominated(ctx, nominator):
                raise commands.BadArgument(
                    "The storytellers cannot be nominated today."
                )
    elif not nominee.can_be_nominated(ctx, nominator):
        raise commands.BadArgument("{nominee.nick} cannot be nominated today.")


def _check_valid_nominator(ctx: Context, nominator: Player, nominee: Player):
    """Check that nominator is a valid nominator, else raise an exception."""
    if not (
        nominator.can_nominate(ctx)
        or nominee.character_type(ctx) == "traveler"
        or nominator.character_type(ctx) == "storyteller"
    ):
        raise ValueError("nominator already nominated")


async def _determine_nominee(ctx: Context, nominee_str: str) -> Player:
    """Determine the nominee from the string."""
    if "storyteller" in nominee_str and ctx.bot.game.script.has_atheist:  #
        # atheist nominations
        nominee = ctx.bot.game.storytellers[0]
    else:
        nominee = await to_player(
            ctx,
            nominee_str,
            only_one=True,
            includes_storytellers=ctx.bot.game.script.has_atheist,
        )
    return nominee


def generate_nomination_message_text(
    ctx: Context,
    nominator: "Player",
    nominee: "Player",
    traveler=False,
    proceed=True,
    majority=0,
    about_to_die: Optional[Tuple[Player, int, int]] = None,
) -> str:
    """Generate the nomination announcement message.

    Parameters
    ----------
    ctx : Context
        The invocation context.
    nominator: Player
        The nominator.
    nominee: Player
        The nominee.
    traveler: bool
        Whether the nominee is a traveler.
    proceed: bool
        Whether the nomination is going to proceed.
    majority: int
        The majority to announce for the vote.
    about_to_die: Optional[Tuple[Player, int, int]]
        The player currently slated to die.

    Returns
    -------
    str
        The message announcing the nomination.
    """
    nominator_mention = (
        "the storytellers"
        if nominator.character_type(ctx) == "storyteller"
        else nominator.member.mention
    )
    nominee_mention = (
        "the storytellers"
        if nominee.character_type(ctx) == "storyteller"
        else nominee.member.mention
    )
    if traveler:  # traveler nominations
        verb = "have" if nominator.character_type(ctx) == "storyteller" else "has"
        message_text = (
            f"{ctx.bot.player_role.mention}, {nominator_mention} {verb} called for"
            f" {nominee_mention}'s exile."
        )

    else:
        verb = "have" if nominee.character_type(ctx) == "storyteller" else "has"
        message_text = (
            f"{ctx.bot.player_role.mention}, {nominee_mention} {verb} been nominated"
            f" by {nominator_mention}."
        )

    if proceed:

        message_text += f" {majority} to "

        if traveler:
            message_text += "exile."
        else:
            message_text += "execute."
            if about_to_die is not None:
                message_text += f" {about_to_die[1]} to tie."
    return message_text
