"""Contains several utilities, generally not for game logic management."""

from typing import Any, List, Tuple, TYPE_CHECKING

from discord import Message, HTTPException
from discord.abc import Messageable
from discord.ext import commands

from lib.typings.context import Context

if TYPE_CHECKING:
    from lib.logic.Game import Game
    from lib.logic.Player import Player


async def aexec(code: str, ctx: Context) -> Any:
    """Execute code asynchronously.

    This is dangerous and should probably not be enabled on the production server.

    Parameters
    ----------
    code : str
        The code to execute.
    ctx : Context
        The invocation context.

    Returns
    -------
    Any
        The output of code.
    """
    with ctx.typing():
        exec(
            f"async def _ex(ctx): " + "".join(f"\n {line}" for line in code.split("\n"))
        )
        return await locals()["_ex"](ctx)


def get_player(game: "Game", idn: int, include_storytellers: bool = True) -> "Player":
    """Find a matching player.

    Parameters
    ----------
    game : Game
        The game to find a player in.
    idn : int
        The player's member's discord ID.
    include_storytellers : bool
        Whether the search for storytellers as well.

    Returns
    -------
    Player
        The matching player if found, else raises an exception.

    Raises
    ------
    ValueError
        If no matching player is found.
    """
    if include_storytellers:
        for st in game.storytellers:
            if st.member.id == idn:
                return st

    for player in game.seating_order:
        if player.member.id == idn:
            return player

    raise ValueError("player not found")


async def get_input(ctx: Context, text: str, timeout: int = 200) -> str:
    """Ask for a response in a given context.

    Parameters
    ----------
    ctx : Context
        The context to ask for a response in.
    text : str
        The text to ask for a response to.
    timeout : int
        The number of seconds to wait for a response.

    Returns
    -------
    str
        The content of the first message sent in ctx.channel by ctx.author.
    """
    await safe_send(ctx, text)
    out = await ctx.bot.wait_for(
        "message",
        check=(lambda x: x.author == ctx.author and x.channel == ctx.channel),
        timeout=timeout,
    )

    if out.content.lower() == "cancel":
        raise ValueError("cancelled")

    if out.content.startswith(ctx.bot.command_prefix):
        raise ValueError("command called")

    return out.content


async def get_bool_input(ctx: Context, text: str, timeout: int = 200) -> bool:
    """Ask for a boolean response in a given context.

    Parameters
    ----------
    ctx : Context
        The context to ask for a response in.
    text : str
        The text to ask for a response to.
    timeout : int
        The number of seconds to wait for a response.

    Returns
    -------
    bool
        Whether the reply was positive or negative.
    """
    while True:
        try:
            return to_bool(await get_input(ctx, text, timeout))
        except commands.BadArgument as e:
            await safe_send(ctx, str(e))
            # then continue


def str_cleanup(text: str, chars: Tuple[str] = (",", " ", "-", "'", "_")) -> str:
    """Remove all instances of chars in str and capitalize the following letter."""
    text_list = [text]
    for char in chars:
        temp_list = []
        for x in text_list:
            for y in x.split(char):
                temp_list.append(y)
        text_list = temp_list
    return "".join([x.capitalize() for x in text_list])


async def safe_send(target: Messageable, msg: str) -> Message:
    """Send a message with protection from message length errors.

    Functionally a wrapper of target.send.

    Parameters
    ----------
    target : Messageable
        The object to send the message to.
    msg : str
        The message to be sent.

    Returns
    -------
    Message
        The first message sent this way.
    """
    try:
        return await target.send(msg)

    except HTTPException as e:
        if e.code == 50035:

            n = len(msg) // 2
            out = await safe_send(target, msg[:n])
            await safe_send(target, msg[n:])
            return out

        raise


def list_to_plural_string(initial_list: List[str], alt: str) -> Tuple[str, bool]:
    """Convert a list of strings into a list with appropriate punctuation.

    Parameters
    ----------
    initial_list : List[str]
        A list of strings to be concatenated.
    alt : str
        The language to use if initial_list is empty.

    Returns
    -------
    Tuple[str, bool]
        The concatenated string, and whether to use plural grammar.
    """
    if len(initial_list) == 0:
        return alt, False
    if len(initial_list) == 1:
        return initial_list[0], False
    if len(initial_list) == 2:
        return initial_list[0] + " and " + initial_list[1], True
    return ", ".join(initial_list[:-1]) + ", and " + initial_list[-1], True


def to_bool(argument: str) -> bool:
    """Convert an argument to a boolean."""
    if argument.lower() in ("y", "ye", "yes", "ok", "true", "t"):
        return True

    if argument.lower() in ("n", "no", "nope", "false", "f"):
        return False

    raise commands.BadArgument(
        f"{argument} is not a valid response. Try 'yes', 'y', 'no', or 'n'."
    )


def safe_bug_report(ctx: Context) -> bool:
    """Determine if the context is safe to send arbitrary error messages.

    For instance, it's unsafe to send those messages in public.
    This is because they may contain privileged game info.
    """
    return ctx.guild is None and ctx.author in ctx.bot.storyteller_role.members
