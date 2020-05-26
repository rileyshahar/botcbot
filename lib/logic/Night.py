"""Contains the Night class."""
from random import shuffle
from typing import TYPE_CHECKING, List, Tuple

from lib.abc import NightOrderMember
from lib.exceptions import InvalidMorningTargetError
from lib.logic.Day import Day
from lib.typings.context import Context
from lib.utils import list_to_plural_string, safe_bug_report, safe_send

if TYPE_CHECKING:
    from lib.logic.Player import Player
    from lib.logic.Game import Game


def _get_minion_demon_text(ctx: Context) -> Tuple[Tuple[str, bool], Tuple[str, bool]]:
    assert ctx.bot.game  # mypy-proofing
    minions = [
        player.nick
        for player in ctx.bot.game.seating_order
        if player.is_status(ctx.bot.game, "minion")
    ]
    minion_text = list_to_plural_string(minions, "")
    demons = [
        player.nick
        for player in ctx.bot.game.seating_order
        if player.is_status(ctx.bot.game, "demon")
    ]
    demon_text = list_to_plural_string(demons, "no one")
    return minion_text, demon_text


class _MinionInfo(NightOrderMember):
    async def morning_call(self, ctx: Context) -> str:
        """Determine the morning call."""
        if len(ctx.bot.game.seating_order) < 7:  # teensyville
            return ""
        minion_text, demon_text = _get_minion_demon_text(ctx)
        if not minion_text[0]:  # there are no minions
            return ""
        s = ""
        if minion_text[1]:
            s = "s"
        return f"Tell the Minion{s} ({minion_text[0]}) the Demon ({demon_text[0]})."


class _DemonInfo(NightOrderMember):
    async def morning_call(self, ctx: Context) -> str:
        """Determine the morning call."""
        if len(ctx.bot.game.seating_order) < 7:  # teensyville
            return ""
        minion_text, demon_text = _get_minion_demon_text(ctx)
        s = ""
        if minion_text[1]:
            s = "s"
        return (
            f"Tell the Demon ({demon_text[0]}) the Minion{s} "
            f"({minion_text[0]}) and three bluffs."
        )


class _NightEnd(NightOrderMember):
    async def morning_call(self, ctx: Context) -> str:
        """Determine the morning call."""
        return "The next step will start the day."


class Night:
    """Stores information about the night."""

    _order: List[NightOrderMember]

    def __init__(self, game: "Game"):
        self._step = 0
        self._set_order(game)
        self._kills: List["Player"] = []
        self._messages: List[str] = []

    def _set_order(self, game: "Game"):
        if game.day_number == 0:
            night_order = game.script.first_night
        else:
            night_order = game.script.other_nights
        relevant_characters = [
            player.character
            for player in game.seating_order
            if type(player.character) in night_order and not player.ghost(game)
        ]
        relevant_characters = sorted(
            relevant_characters, key=lambda x: night_order.index(type(x))
        )
        self._order = relevant_characters + [_NightEnd()]  # type: ignore
        if game.day_number == 0:
            self._order = [_MinionInfo(), _DemonInfo()] + self._order

    @property
    def _current_character(self) -> NightOrderMember:
        """Determine the current character to check."""
        return self._order[self._step]

    async def current_step(self, ctx: Context):
        """Send a reminder of the current step in the night."""
        message_text = await self._current_character.morning_call(ctx)
        if message_text:
            if safe_bug_report(ctx):
                await safe_send(ctx, message_text)
        else:
            await self._increment_night(ctx)

    async def next_step(self, ctx: Context):
        """Perform the next step in the night."""
        try:
            out_temp = await self._current_character.morning(ctx)
        except InvalidMorningTargetError as e:
            out_temp = e.out
        self._kills += out_temp[0]
        self._messages += out_temp[1]

        await self._increment_night(ctx)

    async def _increment_night(self, ctx):
        self._step += 1
        if self._step >= len(self._order):
            await self._end(ctx)
        else:
            await self.current_step(ctx)

    async def _end(self, ctx: Context):
        for player in ctx.bot.game.seating_order:
            player.morning(ctx.bot.inactive_role)
            effect_list = [x for x in player.effects]
            for effect in effect_list:
                effect.morning_cleanup(ctx)

        # announcements
        # kills
        shuffle(self._kills)
        text = list_to_plural_string([x.nick for x in self._kills], alt="No one")
        await safe_send(
            ctx.bot.channel,
            "{text} {verb} died.".format(text=text[0], verb=("has", "have")[text[1]]),
        )

        # other
        for content in self._messages:
            if content:
                await safe_send(ctx.bot.channel, content, pin=True)

        # start day
        await safe_send(
            ctx.bot.channel,
            f"{ctx.bot.player_role.mention}, wake up!",
            pin=bool(self._kills),
        )

        # end night
        ctx.bot.game.past_nights.append(self)
        ctx.bot.game.current_night = None

        # make the day
        ctx.bot.game.current_day = Day()

        # complete
        if safe_bug_report(ctx):
            await safe_send(ctx, "Successfully started the day.")

    def add(self, character: NightOrderMember):
        """Add player to the order."""
        self._order.insert(self._step + 1, character)
