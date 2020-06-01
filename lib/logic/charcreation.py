"""Contains utilities for character creation."""
from abc import ABC, abstractmethod
from functools import wraps
from typing import TYPE_CHECKING, Callable, List, Optional, Tuple, Type

from discord.ext import commands

from lib.exceptions import InvalidMorningTargetError
from lib.logic.Character import Character
from lib.logic.Effect import Dead, Effect
from lib.logic.playerconverter import to_player
from lib.preferences import load_preferences
from lib.utils import get_input, safe_bug_report, safe_send

if TYPE_CHECKING:
    from lib.logic.Player import Player
    from lib.logic.Game import Game
    from lib.typings.context import Context


async def select_target(
    ctx: "Context",
    question: str,
    allow_none: bool = True,
    condition: Callable[["Player", "Game"], bool] = lambda x, y: True,
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
    condition: Callable[["Player", Game], bool]
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


def if_functioning(run_if_drunkpoisoned):
    """Stop character methods if the character is not functioning."""
    # noinspection PyMissingOrEmptyDocstring
    def outer_wrapper(func):
        # noinspection PyMissingOrEmptyDocstring
        @wraps(func)
        async def inner_wrapper(character: Character, ctx: "Context", *args, **kwargs):
            if character.parent.functioning(ctx.bot.game):
                return await func(character, ctx, *args, **kwargs)
            if safe_bug_report(ctx):
                if character.parent.ghost(ctx.bot.game):
                    status = "dead"
                elif character.parent.is_status(ctx.bot.game, "drunk"):
                    status = "drunk"
                elif character.parent.is_status(ctx.bot.game, "poisoned"):
                    status = "poisoned"
                else:
                    status = "not functioning"
                if run_if_drunkpoisoned and status in ("drunk", "poisoned"):
                    kwargs["enabled"] = False
                    kwargs["epithet_string"] = f"({status})"
                    return await func(character, ctx, *args, **kwargs)
                pronouns = load_preferences(character.parent).pronouns
                await safe_send(
                    ctx,
                    "Skipping {epithet}, as {pronoun} {verb} {status}.".format(
                        epithet=character.parent.epithet,
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
            return await getattr(Character(None), func.__name__)(ctx, *args, **kwargs)

        return inner_wrapper

    return outer_wrapper


def onetime_use(func):
    """Stop character methods if the character has used their ability."""
    # noinspection PyMissingOrEmptyDocstring
    @wraps(func)
    async def wrapper(character: Character, ctx: "Context", *args, **kwargs):
        if not character.parent.is_status(ctx.bot.game, "used_ability"):
            return await func(character, ctx, *args, **kwargs)
        if safe_bug_report(ctx):
            pronouns = load_preferences(character.parent).pronouns
            await safe_send(
                ctx,
                (
                    "Skipping {epithet}, as "
                    "{subjective} {verb} used {posessive} ability."
                ).format(
                    epithet=character.parent.epithet,
                    subjective=pronouns[0],
                    verb=["has", "have"][pronouns[5]],
                    posessive=pronouns[2],
                ),
            )
        return await getattr(Character(None), func.__name__)(ctx, *args, **kwargs)

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
    Also, it allows much more granular control than mixins.
    """

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


@class_decorator_factory("evening_cleanup")
def evening_delete(*args):
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


@class_decorator_factory("morning_cleanup")
def morning_delete(*args):
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


@class_decorator_factory("source_drunkpoisoned_cleanup")
def source_drunkpoisoned_disable(*args):
    """Disable the wrapped effect when its source stops is drunk or poisoned."""
    args[0].disable(args[1])


@class_decorator_factory("source_death_cleanup")
def source_death_delete(*args):
    """Delete the wrapped effect when its source dies."""
    args[0].delete(args[1])


@class_decorator_factory("source_starts_functioning")
def source_functioning_enable(*args):
    """Enable the wrapped effect when its source restarts functioning."""

    def enabler_func():
        """Disable the effect."""
        args[0].disabled = False

    args[0].turn_on(args[1], enabler_func)


def generic_ongoing_effect(effect: Type["Effect"]):
    """Delete the effect on source death and disable it on source drunkpoisoning."""
    return source_functioning_enable()(
        source_drunkpoisoned_disable()(source_death_delete()(effect))
    )


def _condition_wrapper(condition):
    @wraps(condition)
    def wrapper(player: "Player", game: "Game"):
        """Return true if player exists and condition is met, else raise an exception."""
        if player:
            return condition(player, game)
        raise InvalidMorningTargetError

    return wrapper


async def add_targeted_effect(
    character: Character,
    ctx: "Context",
    effect: Type["Effect"],
    verb: str,
    *,
    condition: Callable[["Player", "Game"], bool] = lambda x, y: True,
    allow_none: bool = True,
    enabled: bool = True,
    epithet_string: str = "",
) -> Tuple[List["Player"], List[str]]:
    """Choose a target and add an effect.

    Parameters
    ----------
    character : Character
        The character who controls the effect.
    ctx : "GameContext"
        The context.
    effect : Type["Effect"]
        The type of effect to add.
    verb : str
        The verb describing the effect, ex "kill" or "poison". 
    condition : Callable[["Player", "Game"], bool]
        A condition the target must satisfy.
        This should return InvalidMorningTargetError if not met.
    allow_none : bool
        Whether to allow no target.
    enabled : bool
        Whether to enable the effect.
    epithet_string : str
        A string to add to the character's epithet, for instance "poisoner".

    Returns
    -------
    Tuple[List["Player"], List[str]]
        A list of players killed, and a list of messages to add to the end of the night.

    """
    if allow_none:
        condition = _condition_wrapper(condition)
    target = await select_target(
        ctx,
        f"Who did {character.parent.formatted_epithet(epithet_string)}, {verb}?",
        condition=condition,
    )
    effect_object = target.add_effect(ctx.bot.game, effect, character.parent)
    if not enabled:
        effect_object.disable(ctx.bot.game)
    if issubclass(effect, Dead):
        return [target], []
    else:
        return [], []


@_condition_wrapper
def _kill_condition(target: "Player", game: "Game"):
    if not (target.is_status(game, "safe_from_demon") or target.ghost(game)):
        return True
    raise InvalidMorningTargetError


async def kill_selector(
    character: Character, ctx: "Context", kill_effect: Type[Effect] = Dead
) -> Tuple[List["Player"], List[str]]:
    """Perform a nightly kill.

    Parameters
    ----------
    character : Character
        The character controlling the effect.
    ctx : "Context"
        The context.
    kill_effect : Type[Effect]
        The effect representing the kill.

    Returns
    -------
    Tuple[List["Player"], List[str]]
    """
    return await add_targeted_effect(
        character, ctx, kill_effect, "kill", condition=_kill_condition
    )


class MorningTargetCallMixin(Character):
    """Mixin for characters which target in the morning.

    Attributes
    ----------
    _TARGETS : int
        The number of character they target in the morning.
    _MORNING_CONDITION_STRING : str
        A string representing a condition for their targets.
    _OPTIONAL_TARGETER : bool
        Whether they can choose not to target.
    """

    _TARGETS = 1
    _MORNING_CONDITION_STRING = ""
    _OPTIONAL_TARGETER = False

    @if_functioning(True)
    async def morning_call(self, ctx: "Context"):
        """Determine the morning call."""
        condition = self._MORNING_CONDITION_STRING
        if condition:
            condition += " "
        optional = ", or pass" if self._OPTIONAL_TARGETER else ""
        if self._TARGETS == 1:
            if condition.startswith(("a", "e", "i", "o", "u")):
                number_word = "an"
            else:
                number_word = "a"
            plural = ""
        else:
            plural = "s"
            number_word = str(self._TARGETS)
        target_string = f"{number_word} {condition}player{plural}{optional}"

        return f"Ask {self.parent.epithet}, to choose {target_string}."


class MorningTargeterMixin(MorningTargetCallMixin, ABC):
    """Mixin for characters which target and add an effect to a single player.

    Attributes
    ----------
    _MORNING_EFFECT : Type[Effect]
        The effect they apply in the morning.

    _MOTNING_TARGET_STRONG : str
        A very explaining what their effect does, for instance "Kill".
    """

    @classmethod
    @property
    @abstractmethod
    def _MORNING_EFFECT(cls) -> Type[Effect]:
        raise NotImplementedError

    @classmethod
    @property
    @abstractmethod
    def _MORNING_TARGET_STRING(cls) -> str:
        raise NotImplementedError

    @if_functioning(True)
    async def morning(
        self, ctx, enabled=True, epithet_string=""
    ) -> Tuple[List["Player"], List[str]]:
        """Apply the effect to a chosen target."""
        return await add_targeted_effect(
            self,
            ctx,
            self._MORNING_EFFECT,
            self._MORNING_TARGET_STRING,
            enabled=enabled,
            epithet_string=epithet_string,
        )


class _Correct(Effect):
    _name = "Correct"


class _Wrong(Effect):
    _name = "Wrong"


class SeesTwo(Character, ABC):
    """Handles common functionality between Investigator, Librarian, and Washerwoman."""

    @classmethod
    @property
    @abstractmethod
    def _SEES(cls) -> str:
        raise NotImplementedError

    def _condition_literal(self, player: "Player", game: "Game") -> bool:
        return player.is_status(game, self._SEES.lower(), registers=True)

    # noinspection PyPep8Naming

    def _condition(self, player: "Player", game: "Game") -> bool:
        """Determine whether player registers as a townsfolk."""
        if self._condition_literal(player, game):
            return True
        err = f"{player.nick} is not a"
        if self._SEES.startswith(("a", "e", "i", "o", "u")):
            err += "n"
        raise commands.BadArgument(err + f" {self._SEES}.")

    @if_functioning(True)
    async def morning_call(
        self, ctx: "Context", enabled=True, epithet_string=""
    ) -> str:
        """Determine the morning call."""
        out = f"Tell {self.parent.formatted_epithet(epithet_string)}, "
        if enabled:
            out += f"a correct and an incorrect {self._SEES}."
        else:
            out += "any two players."
        return out

    @if_functioning(True)
    async def morning(self, ctx: "Context", enabled=True, epithet_string=""):
        await add_targeted_effect(
            self,
            ctx,
            _Correct,
            f"see as the correct {self._SEES}",
            enabled=enabled,
            epithet_string=epithet_string,
            condition=self._condition,
        )
        await add_targeted_effect(
            self,
            ctx,
            _Wrong,
            f"see as the incorrect {self._SEES}",
            enabled=enabled,
            epithet_string=epithet_string,
        )
        return [], []
