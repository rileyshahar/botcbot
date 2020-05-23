"""Constains the Night class."""
from random import shuffle
from typing import List, TYPE_CHECKING

from lib.abc import NightOrderMember
from lib.exceptions import InvalidMorningTargetError
from lib.logic.Day import Day
from lib.typings.context import Context
from lib.utils import safe_send, list_to_plural_string, safe_bug_report

if TYPE_CHECKING:
    from lib.logic.Player import Player
    from lib.logic.Game import Game


class Night:

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
        if game.day_number == 0:
            relevant_characters += [x() for x in night_order[:2]]
        self._order = sorted(
            relevant_characters, key=lambda x: night_order.index(type(x))
        )

    @property
    def _current_character(self) -> NightOrderMember:
        """Determine the current character to check."""
        return self._order[self._step]

    async def current_step(self, ctx: Context):
        """Send a reminder of the current step in the night."""
        message_text = await self._current_character.morning_call(ctx)
        if message_text:
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
        kill_msg = await safe_send(
            ctx.bot.channel,
            "{text} {verb} died.".format(text=text[0], verb=("has", "have")[text[1]]),
        )

        # other
        for content in self._messages:
            if content:
                msg = await safe_send(ctx.bot.channel, content)
                await msg.pin()

        # start day
        await safe_send(
            ctx.bot.channel, f"{ctx.bot.player_role.mention}, wake up!",
        )
        if self._kills:
            await kill_msg.pin()

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
