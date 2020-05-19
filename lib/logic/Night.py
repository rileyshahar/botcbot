"""Constains the Night class."""
from random import shuffle
from typing import List, TYPE_CHECKING

from lib.exceptions import InvalidMorningTargetError
from lib.logic.Day import Day
from lib.typings.context import Context
from lib.utils import safe_send, list_to_plural_string, safe_bug_report

if TYPE_CHECKING:
    from lib.logic.Player import Player
    from lib.logic.Game import Game


class Night:

    _order: List["Player"]

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
        relevant_players = [
            player
            for player in game.seating_order
            if type(player.character) in night_order and not player.ghost(game)
        ]
        self._order = sorted(
            relevant_players, key=lambda x: night_order.index(type(x.character))
        )

    @property
    def _current_player(self) -> "Player":
        """Determine the current character to check."""
        return self._order[self._step]

    async def current_step(self, ctx: Context):
        await safe_send(ctx, self._current_player.character.morning_call())

    async def next_step(self, ctx: Context):
        try:
            out_temp = await self._current_player.character.morning(ctx)
        except InvalidMorningTargetError as e:
            out_temp = e.out
        self._kills += out_temp[0]
        self._messages += out_temp[1]

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

    def add(self, player: "Player"):
        """Add player to the order."""
        self._order.insert(self._step + 1, player)
