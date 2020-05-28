"""Contains several pseudo-converters for coercing strings to custom types."""

from typing import TYPE_CHECKING, List, Optional, Type

from discord.ext import commands

from lib.logic.Script import script_list
from lib.utils import str_cleanup
from resources.basegame import characters

try:
    from resources.playtest import characters as playtestcharacters
except ImportError:
    playtestcharacters = None


if TYPE_CHECKING:
    from lib.logic.Script import Script
    from lib.logic.Character import Character
    from lib.typings.context import Context


def to_character(
    ctx: "Context", argument: str, script: Optional["Script"] = None
) -> Type["Character"]:
    """Convert a string to a Character class with a matching name.

    The string must be an exact match, except capitalization and special characters.

    Parameters
    ----------
    ctx: Context
        The invocation context.
    argument : str
        The string to match to a character.
    script : Optional[Script]
        The script to search for the character on.

    Returns
    -------
    Type["Character"]
        The matching character class.
    """
    text = str_cleanup(argument)

    if script:
        character: Type["Character"]
        for character in script.character_list:
            if text == character.__name__:
                return character
        raise commands.BadArgument(
            f'Character "{argument}" not found on the script {script.name}.'
        )

    try:
        return getattr(characters, text)
    except AttributeError:
        if (
            ctx.bot.playtest_role
            in ctx.bot.server.get_member(ctx.message.author.id).roles
        ):
            try:
                character = getattr(playtestcharacters, text)
                if ctx.bot.playtest:
                    raise commands.BadArgument(
                        "Playtest characters are not enabled on this bot."
                    )
                return character
            except AttributeError:
                pass
        raise commands.BadArgument(f'Character "{argument}" not found.')


def to_character_list(
    ctx: "Context", arguments: List[str], script: Optional["Script"] = None
) -> List[Type["Character"]]:
    """Convert a list of strings into characters with corresponding names."""
    out = []  # type: List[Type[Character]]
    for character in arguments:
        out.append(to_character(ctx, character, script))
    return out


def to_script(ctx: "Context", argument: str) -> "Script":
    """Convert a string to a Script with a matching name.

    The match does not have to be exact. The string must be contained in script.name.

    Parameters
    ----------
    ctx : Context
        The invocation context.
    argument : str
        The string to match to a script.

    Returns
    -------
    Script
        The matching script.
    """
    for script in script_list(
        ctx,
        playtest=ctx.bot.playtest_role
        in ctx.bot.server.get_member(ctx.message.author.id).roles,
    ):
        if argument.lower() in script.name.lower() or argument.lower() in [
            x.lower() for x in script.aliases
        ]:
            if script.playtest and not ctx.bot.playtest:
                raise commands.BadArgument(
                    "Playtest scripts are not enabled on this bot."
                )
            return script
    raise commands.BadArgument(f'Script "{argument}" not found.')
