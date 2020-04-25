"""Contains tools for managing game logic."""

from functools import wraps
from typing import List, Optional, Type, Callable, TYPE_CHECKING

import numpy as np
from discord.ext import commands

from lib.logic.Character import Character
from lib.logic.playerconverter import to_player
from lib.preferences import load_preferences
from lib.typings.context import Context
from lib.utils import safe_send, get_input, safe_bug_report

if TYPE_CHECKING:
    from lib.logic.Player import Player
    from lib.logic.Effect import Effect

# TODO: sort these into more sensible locations


def generate_game_info_message(order: List["Player"], ctx: Context) -> str:
    """Generate a seating order message.

    Parameters
    ----------
    order : List[Player]
        The order of players.
    ctx : Context
        The invocation context.

    Returns
    -------
    str
        A seating order message representing order.
    """
    message_text = _generate_seating_order_message(ctx, order)
    message_text += _generate_distribution_message(order)
    return message_text


def _generate_seating_order_message(ctx, order):
    message_text = "**Seating Order:**"
    for player in order:
        message_text += _generate_player_line(ctx, player)
    return message_text


def _generate_player_line(ctx, player):
    message_text = "\n"

    if player.ghost(ctx, registers=True):
        message_text += f"~~{player.nick}~~ "

        dead_votes = "O" * player.dead_votes
        if dead_votes == "":
            dead_votes = "X"
        message_text += dead_votes

    else:
        message_text += player.nick
    message_text += player.character.seating_order_addendum
    return message_text


def _generate_distribution_message(order):
    n = len([x for x in order if not x.character_type == "traveler"])
    if n == 5:
        distribution = ("3", "0", "1")
    elif n == 6:
        distribution = ("3", "1", "1")
    elif 7 <= n <= 15:
        o = int((n - 1) % 3)
        m = int(np.floor((n - 1) / 3) - 1)
        distribution = (str(n - (o + m + 1)), str(o), str(m))
    else:
        distribution = ("Unknown", "Unknown", "Unknown")
    outsider_plural = "s" if distribution[1] != 1 else ""
    minion_plural = "s" if distribution[2] != 1 else ""
    message_text = (
        f"\n\nThere are {str(n)} non-Traveler players. The default distribution is "
        f"{distribution[0]} Townsfolk, {distribution[1]} Outsider{outsider_plural}, "
        f"{distribution[2]} Minion{minion_plural}, and 1 Demon."
    )
    return message_text


async def select_target(
    ctx: Context,
    question: str,
    allow_none: bool = True,
    condition: Callable[["Player", Context], bool] = lambda x, y: True,
    **kwargs,
) -> Optional["Player"]:
    """Ask for a target.

    Parameters
    ----------
    ctx : Context
        The invocation context to ask for a target in.
    question : str
        The question to ask.
    allow_none : bool
        Whether "no one" is a valid option.
    condition: Callable[["Player", ctx], bool]
        A condition to pass to get_player.

    Returns
    -------
    Optional["Player"]
        The chosen player, or None.

    """
    while True:
        try:
            answer = await get_input(ctx, question)
            if allow_none and answer.lower() in [
                "none",
                "no one",
                "no-one",
                "noone",
                "nobody",
                "nothing",
                "no",
            ]:
                return None
            return await to_player(ctx, answer, condition=condition, **kwargs)
        except commands.BadArgument as e:
            await safe_send(
                ctx,
                str(e)
                + (
                    ' Please try again. You can also respond with "cancel" '
                    'or most variants of "no one".'
                ),
            )


# Decorators for help with characters and effects
def if_functioning(run_if_drunkpoisoned):
    """Stop character methods if the character is not functioning."""
    # noinspection PyMissingOrEmptyDocstring
    def outer_wrapper(func):
        # noinspection PyMissingOrEmptyDocstring
        @wraps(func)
        async def inner_wrapper(*args, **kwargs):
            if args[0].parent.functioning(args[1]):
                return await func(*args, **kwargs)
            if safe_bug_report(args[1]):
                if args[0].parent.ghost(args[1]):
                    status = "dead"
                elif args[0].parent.is_status(args[1], "drunk"):
                    status = "drunk"
                elif args[0].parent.is_status(args[1], "poisoned"):
                    status = "poisoned"
                else:
                    status = "not functioning"
                if run_if_drunkpoisoned and status in ("drunk", "poisoned"):
                    kwargs["enabled"] = False
                    kwargs["epithet_string"] = f"({status})"
                    return await func(*args, **kwargs)
                pronouns = load_preferences(args[0].parent).pronouns
                await safe_send(
                    args[1],
                    "Skipping {epithet}, as {pronoun} {verb} {status}.".format(
                        epithet=args[0].parent.epithet,
                        pronoun=pronouns[0],
                        verb=("is", "are")[pronouns[5]],
                        status=status,
                    ),
                )

            # this return is hella janky but basically we want this to work for any
            # of the character methods (ex morning, evening) and they have different
            # return types so we need to grab whatever the generic return is.
            # the character initializes with no parent to let us check in the method
            # if it's actually being called or just being called to get the return
            # so we can hide side effects in an "if self.parent" block
            return await getattr(Character(None), func.__name__)(*args[1:], **kwargs)

        return inner_wrapper

    return outer_wrapper


def onetime_use(func):
    """Stop character methods if the character has used their ability."""
    # noinspection PyMissingOrEmptyDocstring
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not args[0].parent.is_status(args[1], "used_ability"):
            return await func(*args, **kwargs)
        if safe_bug_report(args[1]):
            pronouns = load_preferences(args[0].parent).pronouns
            await safe_send(
                args[1],
                (
                    "Skipping {epithet}, as "
                    "{subjective} {verb} used {posessive} ability."
                ).format(
                    epithet=args[0].parent.epithet,
                    subjective=pronouns[0],
                    verb=["has", "have"][pronouns[5]],
                    posessive=pronouns[2],
                ),
            )
        return await getattr(Character(None), func.__name__)(*args[1:], **kwargs)

    return wrapper


def class_decorator_factory(func_name):
    """Create decorators to prefix functions of classes and give them certain attributes.

    For example:
    class A:
        def print_secret_word(self):
            print('hello')

    @class_decorator_factory('print_secret_word')
    def decorator_example(*args, **kwargs):
        print('world')

    @class_decorator_factory('print_a')
    def decorator_example_two(*args, **kwargs):
        print(args[0].a)

    @decorator_example(('a', 1))
    @decorator_example_two()
    class B(A):
        pass

    obj = B()
    obj.print_secret_word() # hello world
    obj.print_a # 1

    Why is this using decorators and not subclasses?
    This more easily allows us to append the wrapped function to an existing function.
    """
    # TODO: refactor all this code to use subclasses
    # because why the fuck did I think decorators were a good idea

    def wrapper_func_getter(wrapper_func):
        """Get the actual wrapper function."""

        def attribute_getter(*attributes):
            """Get a list of tuples of attributes and values to create for the class."""

            def class_decorator(cls):
                """Get the class to decorate."""

                def outer_wrapper(final_func):
                    """Get the function to decorate."""

                    def inner_wrapper(*args, **kwargs):
                        """Run the actual function then the wrapper function."""
                        final_func(*args, **kwargs)
                        wrapper_func(*args, **kwargs)

                    return inner_wrapper

                try:
                    setattr(cls, func_name, outer_wrapper(getattr(cls, func_name)))
                except AttributeError:
                    setattr(cls, func_name, wrapper_func)
                for attribute in attributes:
                    setattr(cls, attribute[0], attribute[1])
                return cls

            return class_decorator

        return attribute_getter

    return wrapper_func_getter


# noinspection PyUnusedLocal
@class_decorator_factory("evening_cleanup")
def evening_delete(*args, **kwargs):
    """Delete the wrapped effect at the end of the day.

    Should be called with a "days" attribute; deletes after that many days.
    """
    try:
        if args[0].days == 1:
            args[0].delete(args[1])
        else:
            args[0].days -= 1
    except AttributeError:  # if days is not set
        args[0].delete(args[1])


# noinspection PyUnusedLocal
@class_decorator_factory("morning_cleanup")
def morning_delete(*args, **kwargs):
    """Delete the wrapped effect at the start of the day.

    Should be called with a "days" attribute; deletes after that many days.
    """
    try:
        if args[0].days == 1:
            args[0].delete(args[1])
        else:
            args[0].days -= 1
    except AttributeError:  # if days is not set
        args[0].delete(args[1])


# noinspection PyUnusedLocal
@class_decorator_factory("source_drunkpoisoned_cleanup")
def source_drunkpoisoned_disable(*args, **kwargs):
    """Disable the wrapped effect when its source stops is drunk or poisoned."""
    args[0].disable(args[1])


# noinspection PyUnusedLocal
@class_decorator_factory("source_death_cleanup")
def source_death_delete(*args, **kwargs):
    """Delete the wrapped effect when its source dies."""
    args[0].delete(args[1])


# noinspection PyUnusedLocal
@class_decorator_factory("source_starts_functioning")
def source_functioning_enable(*args, **kwargs):
    """Enable the wrapped effect when its source restarts functioning."""
    args[0].disabled = False


def generic_ongoing_effect(effect: Type["Effect"]):
    """Delete the effect on source death and disable it on source drunkpoisoning."""
    return source_functioning_enable()(
        source_drunkpoisoned_disable()(source_death_delete()(effect))
    )
