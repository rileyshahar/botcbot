"""Contains the Game class."""

from typing import List, Optional, TYPE_CHECKING

from discord import Message
from discord.ext import commands

from lib.logic.Day import Day
from lib.logic.Night import Night
from lib.logic.Player import Player
from lib.logic.tools import generate_game_info_message
from lib.typings.context import Context

if TYPE_CHECKING:
    from lib.logic.Script import Script


class Game:
    """Stores information about a game.

    Parameters
    ----------
    seating_order : List[Player]
        The game's players, in _order.
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
        self.past_nights = []  # type: List[Night]
        self.current_night = None  # type: Optional[Night]
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

    @property
    def not_active(self) -> List[Player]:
        """Determine the players who have not spoken today."""
        return [player for player in self.seating_order if not player.has_spoken]

    @property
    def to_nominate(self) -> List[Player]:
        """Determine the players who have not spoken today."""
        return [
            player
            for player in self.seating_order
            if player.can_nominate(self) and not player.has_skipped
        ]

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
            raise commands.BadArgument(
                "The new and old seating orders have differing lengths."
            )

        # Edit the message
        await self.seating_order_message.edit(
            content=generate_game_info_message(new_seating_order, ctx.bot.game)
        )

        # Update seating order
        self.seating_order = new_seating_order

    async def start_night(self, ctx: Context):
        """Start a new night."""

        self.current_night = Night(self)
        await self.current_night.current_step(ctx)
