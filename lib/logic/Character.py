"""Contains the Character and Storyteller classes and several Character subclasses."""

import json
from abc import ABC
from typing import TYPE_CHECKING, Dict, List, Tuple, Type

from discord.ext import commands

from lib.abc import NightOrderMember
from lib.logic.Effect import (Dead, DemonEffect, Evil, Good, MinionEffect,
                              OutsiderEffect, StorytellerEffect,
                              TownsfolkEffect, TravelerEffect)
from lib.utils import safe_send

if TYPE_CHECKING:
    from lib.logic.Effect import Effect
    from lib.logic.Player import Player
    from lib.typings.context import Context


class Character(NightOrderMember):
    """A generic character.

    Parameters
    ----------
    parent : Player
        The player the character belongs to.

    Attributes
    ----------
    default_effects : List[Type[Effect]]
        The effects a character starts with.
    parent: Player
    """

    name: str = "Character"
    playtest: bool = False
    default_effects: List[Type["Effect"]]

    def __init__(self, parent: "Player"):
        self.parent = parent
        self.default_effects = []

    @property
    def seating_order_addendum(self):
        """Determine the seating order addendum."""
        return ""

    async def morning(self, ctx: "Context") -> Tuple[List["Player"], List[str]]:
        """Call at the start of each day. Processes night actions.

        Parameters
        ----------
        ctx : Context
            The invocation context.

        Returns
        -------
        List[Player]
            Players killed by the character.
        str
            A non-kill message to broadcast at the start of the day.
        """
        return [], []

    # noinspection PyUnusedLocal
    async def nomination(
        self, ctx: "Context", nominee: "Player", nominator: "Player",
    ) -> bool:
        """Call at the start of each nomination.

        Parameters
        ----------
        ctx : Context
            The invocation context.
        nominee: Player
            The nominee.
        nominator: Player
            The nominator.

        Returns
        -------
        bool
            Whether to go through with the nomination.
        """
        return True

    async def evening(self, ctx: "Context"):
        """Call at the end of each day.

        Parameters
        ----------
        ctx : Context
            The invocation context.
        """
        pass

    @classmethod
    def _char_info(cls) -> Dict:
        if not cls.playtest:
            with open("resources/basegame/character_info.json", "r") as fp:
                return json.load(fp)[cls.name]
        else:
            with open("resources/d/character_info.json", "r") as fp:
                return json.load(fp)[cls.name]

    @classmethod
    def rules_text(cls) -> str:
        """Generate the character's rules text."""
        try:
            return cls._char_info()["rules"]
        except KeyError:
            return "Rules text not found."

    async def morning_call(self, ctx: "Context") -> str:
        """Generate the character's initial morning call.

        If an empty string is returned, skip the character.

        Notes
        -----
        This is a coroutine so it will be awaited when decorated by if_functioning.
        """
        return ""

    def exile(self, ctx: "Context"):
        """Overridden by traveler."""
        raise commands.BadArgument(f"{self.parent.nick} is not a traveler.")


class Townsfolk(Character, ABC):
    """The Townsfolk class."""

    name: str = "Townsfolk"

    def __init__(self, parent):
        super().__init__(parent)
        self.default_effects += [Good, TownsfolkEffect]


class Outsider(Character, ABC):
    """The Outsider class."""

    name: str = "Outsider"

    def __init__(self, parent):
        super().__init__(parent)
        self.default_effects += [Good, OutsiderEffect]


class Minion(Character, ABC):
    """The Minion class."""

    name: str = "Minion"

    def __init__(self, parent):
        super().__init__(parent)
        self.default_effects += [Evil, MinionEffect]


class Demon(Character, ABC):
    """The Demon class."""

    name: str = "Demon"

    def __init__(self, parent):
        super().__init__(parent)
        self.default_effects += [Evil, DemonEffect]


class Traveler(Character, ABC):
    """The Traveler class."""

    name: str = "Traveler"

    def __init__(self, parent):
        super().__init__(parent)
        self.default_effects += [TravelerEffect]

    @property
    def seating_order_addendum(self):
        """Determine the traveler's seating order addendum."""
        # Cannot be set in __init__ because self.name isn't character-specific there
        return " - " + self.name

    async def exile(self, ctx: "Context"):
        """Exile the traveler."""
        if self.parent.ghost(ctx.bot.game):
            await safe_send(
                ctx.bot.channel,
                f"{self.parent.nick} has been exiled, but is already dead.",
            )

        elif self.parent.is_status(ctx.bot.game, "safe"):
            await safe_send(
                ctx.bot.channel,
                f"{self.parent.nick} has been exiled, but does not die.",
            )

        else:
            await safe_send(
                ctx.bot.channel, f"{self.parent.nick} has been exiled, and dies."
            )
            self.parent.add_effect(ctx.bot.game, Dead, self.parent)


class Storyteller(Character):
    """The Storyteller."""

    name: str = "Storyteller"

    def __init__(self, parent):
        super().__init__(parent)
        self.default_effects += [StorytellerEffect]

    @property
    def seating_order_addendum(self):
        """Determine the seating order addendum."""
        return " - Storyeller"

    async def morning_call(self, ctx: "Context"):
        """Meet ABC requirements."""
        return await super().morning_call(ctx)
