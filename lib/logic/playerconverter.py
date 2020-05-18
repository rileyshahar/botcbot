"""Contains converters replacements from strings to Players and Members."""

from typing import List, Callable, TYPE_CHECKING, Any

from discord import Member
from discord.ext import commands

from lib.preferences import load_preferences
from lib.typings.context import Context
from lib.utils import get_input, get_player
from lib.exceptions import PlayerNotFoundError

if TYPE_CHECKING:
    from lib.logic.Player import Player
    from lib.logic.Game import Game


async def to_member(
    ctx: Context,
    argument: str,
    all_members: bool = True,
    includes_storytellers: bool = False,
    only_one: bool = False,
) -> Member:
    """Convert a string to a member with a matching name.

    The match does not have to be exact.
    The string must be contained in member.nick, member.display_name, or member.name.

    Parameters
    ----------
    ctx : Context
        The invocation context.
    argument : str
        The string to match to a script.
    all_members : bool
        Whether to include all server members or just game players.
    includes_storytellers : bool
        If all_members, whether to include storytellers.
    only_one : bool
        Whether to require exactly one initial match.

    Returns
    -------
    Member
        The matching member.
    """
    # Generate possible matches
    if all_members:
        possibilities = _generate_possibilities(argument, ctx.bot.server.members)
    else:

        if includes_storytellers:
            possibilities = _generate_possibilities(
                argument,
                [
                    x.member
                    for x in ctx.bot.game.seating_order + ctx.bot.game.storytellers
                ],
            )
        else:
            possibilities = _generate_possibilities(
                argument, [x.member for x in ctx.bot.game.seating_order]
            )

    # No matches
    if len(possibilities) == 0:
        raise commands.BadArgument(f'User containing "{argument}" not found.')

    # One match
    if len(possibilities) == 1:
        return possibilities[0]

    if only_one:
        raise commands.BadArgument(
            f"Multiple users match {argument}. Please try again."
        )

    # Multiple matches
    # Request clarification from user
    if argument == "":
        message_text = 'Who do you mean? or say "cancel"'
    else:
        message_text = f'Who do you mean by {argument}? or say "cancel"'
    for person in possibilities:
        message_text += "\n({i}). ".format(i=possibilities.index(person) + 1)
        if (
            ctx.bot.game and person in ctx.bot.game.storytellers
        ) or person in ctx.bot.storyteller_role.members:
            message_text += "**[ST]** "
        message_text += f"{load_preferences(person).nick}"

    # Wait for response
    choice = await get_input(ctx, message_text)

    # If the choice is an int
    try:
        return possibilities[int(choice) - 1]

    # If the choice is a name
    except ValueError:
        return await to_member(ctx, choice)


async def to_member_list(
    ctx: Context,
    arguments: List[str],
    all_members: bool = True,
    includes_storytellers: bool = False,
    only_one: bool = False,
) -> List[Member]:
    """Convert a list of strings into members with corresponding names."""
    out = []  # type: List[Member]
    for member in arguments:
        out.append(
            await to_member(ctx, member, all_members, includes_storytellers, only_one)
        )
    return out


async def to_player(
    ctx: Context,
    argument: str,
    all_members: bool = False,
    includes_storytellers: bool = False,
    only_one: bool = False,
    condition: Callable[["Player", "Game", Any], bool] = lambda x, y: True,
    **kwargs,
) -> "Player":
    """Convert a string to a player with a matching name.

    Functionally just a wrapper of to_member that converts the output to a player.
    The match does not have to be exact.
    The string must be contained in player.nick, player.display_name, or player.name.

    Parameters
    ----------
    ctx : Context
        The invocation context.
    argument : str
        The string to match to a script.
    all_members : bool
        Whether to include all server members or just game players.
    includes_storytellers : bool
        If all_members, whether to include storytellers.
    only_one : bool
        Whether to require exactly one initial match.
    condition: Callable[["Player", Context, Any], bool]
        A condition to require the player to meet. If the condition is not met, should
        raise a commands.BadArgument exception.
        The condition may also take kwargs if necessary.

    Returns
    -------
    Player
        The matching player.
    """
    try:
        player = get_player(
            ctx.bot.game,
            (
                await to_member(
                    ctx, argument, all_members, includes_storytellers, only_one
                )
            ).id,
        )
        if condition(player, ctx.bot.game, **kwargs):
            return player
    except PlayerNotFoundError:
        raise commands.BadArgument(
            f"Multiple players match {argument}. Please try again."
        )


def _generate_possibilities(argument: str, possibilities: List[Member]) -> List[Member]:
    """Determine all members with marching nicknames or usernames.

    Parameters
    ----------
    argument : str
        The string to be matched.
    possibilities : List[Member]
        The possible members to search for matches.

    Returns
    -------
    List[Member]
        The matching members.
    """
    out = []
    for person in possibilities:
        if (
            argument.lower() in load_preferences(person).nick.lower()
            or argument.lower() in person.display_name.lower()
            or argument.lower() in person.name.lower()
        ):
            out.append(person)
    return out
