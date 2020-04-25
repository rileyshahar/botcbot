"""Contains the Character and Storyteller classes and several Character subclasses."""

from typing import List, Tuple, Type, Optional, TYPE_CHECKING

from discord.ext import commands

from resources.basegame.rules_texts import rules_texts

try:
    from resources.playtest.playtest_rules_texts import playtest_rules_texts
except ImportError:
    playtest_rules_texts = {}

from lib.logic.Effect import (
    Dead,
    Good,
    Evil,
    TownsfolkEffect,
    OutsiderEffect,
    MinionEffect,
    DemonEffect,
    TravelerEffect,
    StorytellerEffect,
)
from lib.typings.context import Context
from lib.utils import str_cleanup, safe_send
from lib.preferences import load_preferences

if TYPE_CHECKING:
    from lib.logic.Effect import Effect
    from lib.logic.Player import Player


class Character:
    """A generic character.

    Parameters
    ----------
    parent : Player
        The player the character belongs to.

    Attributes
    ----------
    playtest : bool
        Whether the character is playtest-only.
    name : str
        The character's name.
    default_effects : List[Type[Effect]]
        The effects a character starts with.
    parent: Player
    """

    default_effects: List[Type["Effect"]]

    def __init__(self, parent: Optional["Player"]):
        self.parent = parent
        self.playtest = False
        self.name = "Character"
        self.default_effects = []
        # TODO: think about converting some of these to class attributes
        # the problem is I'm lazy

    @property
    def seating_order_addendum(self):
        """Determine the seating order addendum."""
        return ""

    async def morning(self, ctx: Context) -> Tuple[List["Player"], List[str]]:
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
        # check that this isn't a dummy call from a wrapper to figure out the return
        # see the commenting of tools.if_functioning for more info
        # TODO: pass this as an arg instead
        # the challenge with that is idk how it works with **kwargs
        if self.parent:
            await safe_send(
                ctx,
                (
                    "Skipping {epithet}, as "
                    "{posessive} ability is not handled by the bot."
                ).format(
                    epithet=self.parent.epithet,
                    posessive=load_preferences(self.parent).pronouns[2],
                ),
            )
        return [], []

    # noinspection PyUnusedLocal
    async def nomination(
        self, ctx: Context, nominee: "Player", nominator: "Player",
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

    async def evening(self, ctx: Context):
        """Call at the end of each day.

        Parameters
        ----------
        ctx : Context
            The invocation context.
        """
        pass

    @property
    def rules_text(self) -> str:
        """Generate the character's rules text.

        Can't be defined in __init__ because self.name is Character then.
        """
        try:
            if not self.playtest:
                return rules_texts[str_cleanup(self.name)]
            return playtest_rules_texts[str_cleanup(self.name)]
        except KeyError:
            return "Rules text not found."

    def exile(self, ctx: Context):
        """Overridden by traveler."""
        raise commands.BadArgument(f"{self.parent.nick} is not a traveler.")


class Townsfolk(Character):
    """The Townsfolk class."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Townsfolk"
        self.default_effects = [Good, TownsfolkEffect]


class Outsider(Character):
    """The Outsider class."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Outsider"
        self.default_effects = [Good, OutsiderEffect]


class Minion(Character):
    """The Minion class."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Minion"
        self.default_effects = [Evil, MinionEffect]


class Demon(Character):
    """The Demon class."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Demon"
        self.default_effects = [Evil, DemonEffect]


class Traveler(Character):
    """The Traveler class."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Traveler"
        self.default_effects = [TravelerEffect]

    @property
    def seating_order_addendum(self):
        """Determine the traveler's seating order addendum."""
        # Cannot be set in __init__ because self.name isn't character-specific there
        return " - " + self.name

    async def exile(self, ctx: Context):
        """Exiles the traveler."""
        if self.parent.ghost(ctx):
            await safe_send(
                ctx.bot.channel,
                f"{self.parent.nick} has been exiled, but is already dead.",
            )

        elif self.parent.is_status(ctx, "safe"):
            await safe_send(
                ctx.bot.channel,
                f"{self.parent.nick} has been exiled, but does not die.",
            )

        else:
            await safe_send(
                ctx.bot.channel, f"{self.parent.nick} has been exiled, and dies."
            )
            self.parent.effects.append(Dead(ctx, self.parent, self.parent))


class Storyteller(Character):
    """The Storyteller."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Storyteller"
        self.default_effects = [StorytellerEffect]

    @property
    def seating_order_addendum(self):
        """Determine the seating order addendum."""
        return " - Storyeller"
