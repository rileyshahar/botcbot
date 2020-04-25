"""Contains custom checks."""

from typing import Coroutine, Any, Callable

from discord.ext import commands

from lib.typings.context import Context
from lib.utils import get_player


def is_in_channel() -> Callable[[Any], Coroutine[Any, Any, Any]]:
    """Apply predicate as a check."""

    def predicate(ctx: Context) -> bool:
        """Check if the command was called in the main channel.

        Parameters
        ----------
        ctx : Context
            The invocation context.

        Returns
        -------
        bool
            True if the command succeeds, else raises an exception.

        """
        if ctx.channel == ctx.bot.channel:
            return True
        raise commands.CheckFailure(message="")

    return commands.check(predicate)


def is_dm() -> Callable:
    """Apply predicate as a check."""

    def predicate(ctx: Context) -> bool:
        """Check if the command was called in a DM.

        Parameters
        ----------
        ctx : Context
            The invocation context.

        Returns
        -------
        bool
            True if the command succeeds, else raises an exception.

        """
        if ctx.guild is None:
            return True
        raise commands.CheckFailure(message="")

    return commands.check(predicate)


def is_game() -> Callable:
    """Apply predicate as a check."""

    def predicate(ctx: Context) -> bool:
        """Check if there is a current game.

        Parameters
        ----------
        ctx : Context
            The invocation context.

        Returns
        -------
        bool
            True if the command succeeds, else raises an exception.

        """
        if ctx.bot.game:
            return True
        raise commands.CheckFailure(message="There is no ongoing game.")

    return commands.check(predicate)


def is_not_game() -> Callable:
    """Apply predicate as a check."""

    def predicate(ctx: Context) -> bool:
        """Check if the is no current game.

        Parameters
        ----------
        ctx : Context
            The invocation context.

        Returns
        -------
        bool
            True if the command succeeds, else raises an exception.

        """
        if not ctx.bot.game:
            return True
        raise commands.CheckFailure(message="There is already an ongoing game.")

    return commands.check(predicate)


def is_storyteller() -> Callable:
    """Apply predicate as a check."""

    def predicate(ctx: Context) -> bool:
        """Check if the command author is a storyteller.

        Parameters
        ----------
        ctx : Context
            The invocation context.

        Returns
        -------
        bool
            True if the command succeeds, else raises an exception.

        """
        if ctx.bot.server.get_member(ctx.author.id) in ctx.bot.storyteller_role.members:
            return True
        raise commands.CheckFailure(message="Sorry! Only storytellers can do that.")

    return commands.check(predicate)


def is_player() -> Callable:
    """Apply predicate as a check."""

    def predicate(ctx: Context) -> bool:
        """Check if the command author is a player.

        Parameters
        ----------
        ctx : Context
            The invocation context.

        Returns
        -------
        bool
            True if the command succeeds, else raises an exception.

        """
        if ctx.bot.game:
            try:
                get_player(
                    ctx.bot.game, ctx.message.author.id, include_storytellers=False
                )
                return True
            except ValueError as e:
                if not str(e) == "player not found":
                    raise e
        raise commands.CheckFailure(message="Sorry! Only players can do that.")

    return commands.check(predicate)


def is_day() -> Callable:
    """Apply predicate as a check."""

    def predicate(ctx: Context) -> bool:
        """Check if the game is in day.

        Parameters
        ----------
        ctx : Context
            The invocation context.

        Returns
        -------
        bool
            True if the command succeeds, else raises an exception.

        """
        if ctx.bot.game and ctx.bot.game.current_day:
            return True
        raise commands.CheckFailure(message="It's not day right now.")

    return commands.check(predicate)


def is_night() -> Callable:
    """Apply predicate as a check."""

    def predicate(ctx: Context) -> bool:
        """Check if the game is in night.

        Parameters
        ----------
        ctx : Context
            The invocation context.

        Returns
        -------
        bool
            True if the command succeeds, else raises an exception.

        """
        if ctx.bot.game and not ctx.bot.game.current_day:
            return True
        raise commands.CheckFailure(message="It's already day!")

    return commands.check(predicate)


def pms_open() -> Callable:
    """Apply predicate as a check."""

    def predicate(ctx: Context) -> bool:
        """Check if PMs are open.

        Parameters
        ----------
        ctx : Context
            The invocation context.

        Returns
        -------
        bool
            True if the command succeeds, else raises an exception.

        """
        if (
            ctx.bot.game
            and ctx.bot.game.current_day
            and ctx.bot.game.current_day.is_pms
        ):
            return True
        raise commands.CheckFailure(message="PMs aren't open right now.")

    return commands.check(predicate)


def noms_open() -> Callable:
    """Apply predicate as a check."""

    def predicate(ctx: Context) -> bool:
        """Check if nominations are open.

        Parameters
        ----------
        ctx : Context
            The invocation context.

        Returns
        -------
        bool
            True if the command succeeds, else raises an exception.

        """
        if (
            ctx.bot.game
            and ctx.bot.game.current_day
            and ctx.bot.game.current_day.is_noms
        ):
            return True
        raise commands.CheckFailure(message="Nominations aren't open right now.")

    return commands.check(predicate)


def is_vote() -> Callable:
    """Apply predicate as a check."""

    def predicate(ctx: Context) -> bool:
        """Check if there is an ongoing vote.

        Parameters
        ----------
        ctx : Context
            The invocation context.

        Returns
        -------
        bool
            True if the command succeeds, else raises an exception.

        """
        if (
            ctx.bot.game
            and ctx.bot.game.current_day
            and ctx.bot.game.current_day.current_vote
        ):
            return True
        raise commands.CheckFailure(message="There's no ongoing vote right now.")

    return commands.check(predicate)


def is_not_vote() -> Callable:
    """Apply predicate as a check."""

    def predicate(ctx: Context) -> bool:
        """Check if there is no ongoing vote.

        Parameters
        ----------
        ctx : Context
            The invocation context.

        Returns
        -------
        bool
            True if the command succeeds, else raises an exception.

        """
        if (
            ctx.bot.game
            and ctx.bot.game.current_day
            and not ctx.bot.game.current_day.current_vote
        ):
            return True
        raise commands.CheckFailure(message="There's already an ongoing vote.")

    return commands.check(predicate)
