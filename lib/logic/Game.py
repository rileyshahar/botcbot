"""Contains the Game class."""

from os import remove
from random import shuffle
from typing import List, Optional, TYPE_CHECKING

from discord import Message

from lib.logic.Day import Day
from lib.logic.Player import Player
from lib.logic.tools import generate_game_info_message
from lib.typings.context import Context
from lib.utils import list_to_plural_string, safe_send

if TYPE_CHECKING:
    from lib.logic.Script import Script


class Game:
    """Stores information about a game.

    Parameters
    ----------
    seating_order : List[Player]
        The game's players, in order.
    seating_order_message : Message
        The message announcing the seating order.
    script : Script
        A list of characters on the game's script.
    storytellers : List[Player]
        A list of storytellers on the game's script.

    Attributes
    ----------
    past_days : List[Day]
        The game's previous days.
    current_day : Optional[Day]
        The game's currently active day, or None.
    seating_order
    seating_order_message
    script
    storytellers
    """

    def __init__(
        self,
        seating_order: List[Player],
        seating_order_message: Message,
        script: "Script",
        storytellers: List[Player],
    ):
        self.past_days = []  # type: List[Day]
        self.current_day = None  # type: Optional[Day]
        self.seating_order = seating_order
        self.seating_order_message = seating_order_message
        self.script = script
        self.storytellers = storytellers

    def __getstate__(self) -> dict:
        """Cleanup when pickled."""
        state = self.__dict__.copy()
        state[
            "seating_order_message"
        ] = self.seating_order_message.id  # discord snowflake objects are not picklable
        return state

    @property
    def day_number(self) -> int:
        """Determine the current day number."""
        return len(self.past_days) + int(bool(self.current_day))

    async def reseat(self, ctx: Context, new_seating_order: List[Player]):
        """Modify the seating order and seating order message.

        Parameters
        ----------
        ctx : Context
            The invocation context.
        new_seating_order : List[Player]
            The new seating order to replace self.seating_order.
        """
        # Sanitize inputs
        if len(new_seating_order) != len(self.seating_order):
            raise ValueError("unmatched seating order length")

        # Edit the message
        await self.seating_order_message.edit(
            content=generate_game_info_message(new_seating_order, ctx)
        )

        # Update seating order
        self.seating_order = new_seating_order

    async def startday(self, ctx: Context, kills: List[Player] = None):
        """Handle logic for startday.

        Parameters
        ----------
        ctx : Context
            The invocation context.
        kills : List[Player]
            Players to kill at the beginning of the night.
        """
        ctx.bot.backup("special_backup.pckl")

        kills = kills or []
        messages = []  # type: List[str]

        try:
            # perform kills
            if self.day_number == 0:
                order = self.script.first_night
            else:
                order = self.script.other_nights
            for character in order:
                for player in self.seating_order:
                    if isinstance(player.character, character):
                        out_temp = await player.character.morning(ctx)
                        kills += out_temp[0]
                        messages += out_temp[1]

            # cleanup stuff
            for player in self.seating_order:
                player.morning(ctx)
                effect_list = [x for x in player.effects]
                for effect in effect_list:
                    effect.morning_cleanup(ctx)

            # make the day
            self.current_day = Day()
            await ctx.bot.update_status()

            remove("resources/backup/" + ctx.bot.bot_name + "/special_backup.pckl")

        except Exception:

            await ctx.bot.restore_backup("special_backup.pckl", mute=True)
            remove("resources/backup/" + ctx.bot.bot_name + "/special_backup.pckl")
            raise

        # announcements

        # kills
        shuffle(kills)
        text = list_to_plural_string([x.nick for x in kills], alt="No one")
        kill_msg = await safe_send(
            ctx.bot.channel,
            "{text} {verb} died.".format(text=text[0], verb=("has", "have")[text[1]]),
        )

        # other
        for content in messages:
            if content:
                msg = await safe_send(ctx.bot.channel, content)
                await msg.pin()

        # start day
        await safe_send(
            ctx.bot.channel, f"{ctx.bot.player_role.mention}, wake up!",
        )
        if kills:
            await kill_msg.pin()

        # complete
        await safe_send(ctx, "Successfully started the day.")
        return
