"""Contains the Player class."""

import traceback
import typing
from typing import Optional

from discord import Member, Role
from discord.ext import commands

from lib.logic.Effect import Dead, Effect, Evil, Good
from lib.preferences import load_preferences
from lib.utils import get_input, safe_bug_report, safe_send

if typing.TYPE_CHECKING:
    from lib.logic.Character import Character
    from lib.logic.Game import Game
    from lib.typings.context import GameContext, DayContext


def _get_neighbor(
    game: "Game",
    condition: typing.Callable[["Player", "Game"], bool],
    order: typing.List["Player"],
) -> typing.Optional["Player"]:
    """Determine the first player in _order matching condition."""
    out = None
    for player in order:
        if condition(player, game):
            out = player
            break
    return out


class _UpdateUnnecessaryError(Exception):
    """An update to player activity was unnecessary."""

    pass


async def _update_activity(
    game: "Game",
    updater_func: typing.Callable[["Game"], typing.List["Player"]],
    zero_string: str,
    one_string: str,
):
    """Update a player's activity."""
    try:
        player_list = updater_func(game)
    except _UpdateUnnecessaryError:
        return

    if len(player_list) == 0:
        for st in game.storytellers:
            await safe_send(st.member, f"Everyone has {zero_string}!")

    elif len(player_list) == 1:
        for st in game.storytellers:
            await safe_send(st.member, f"Just {player_list[0].nick} to {one_string}.")


class Player:
    """Stores information about a specific player.

    Parameters
    ----------
    member : Member
        The player's discord member.
    character : Type[Character]
        The player's character.
    position : Optional[int]
        The player's position in the seating order.

    Attributes
    ----------
    effects : List[Effect]
        The effects currently on the player.
    dead_votes : int
        How many dead vote tokens the player has.
    message_history : list[Dict[str, Any]]
        The player's PM history.
        "to": the message's author
        "from": the message's recipient
        "content": the message's content
        "day": the day the message was sent
        "time": the time the message was sent
    has_spoken : bool
        Whether the player has spoken today.
    nominations_today : int
        How many times the player has nominated today.
    has_been_nominated : bool
        Whether the player has been nominated today.
    has_skipped : bool
        Whether the player has skipped today.
    is_inactive : bool
        Whether the player is inactive; generally, whether they have the inactive role.
    member
    character
    """

    # TODO: store all the day-related attributes more compactly

    character: "Character"
    message_history: typing.List[typing.Dict[str, typing.Any]]

    def __init__(
        self,
        member: Member,
        character: typing.Type["Character"],
        position: typing.Optional[int],
    ):
        self.member = member
        self.character = character(self)
        self.position = position
        self.effects = [effect(self, self) for effect in self.character.default_effects]
        self.dead_votes = 1
        self.message_history = []
        self.has_spoken = False
        self.nominations_today = 0
        self.has_been_nominated = False
        self.has_skipped = False
        self.is_inactive = False

    def neighbors(
        self,
        game: "Game",
        condition: typing.Callable[["Player", "Game"], bool] = lambda x, y: True,
    ) -> typing.Tuple[typing.Optional["Player"], typing.Optional["Player"]]:
        """Determine the player's nearest neighbors satisfying a given condition.

        Parameters
        ----------
        game: Game
            The current game.
        condition: typing.Callable[["Player", Game], bool]
            Conditions to be satisfied by the neighbor.

        Returns
        -------
        typing.Tuple["Player", "Player"]
            The upwards neighbor and the downwards neighbor satisfying condition.
        """
        seating_order_excluding_self = (
            # flake8: noqa
            # (this is a false positive), the space is black-enforced
            game.seating_order[self.position + 1 :]
            + game.seating_order[: self.position]
        )
        out1 = _get_neighbor(game, condition, seating_order_excluding_self[::-1])
        out2 = _get_neighbor(game, condition, seating_order_excluding_self)
        return out1, out2

    def source_effects(
        self, game: "Game"
    ) -> typing.Generator["Effect", typing.Any, typing.Any]:
        """Yield all effects for which the player is the source."""
        for player in game.seating_order:
            for effect in player.effects:
                if effect.source_player == self:
                    yield effect

    # Aliases for is_status and registers_status and related
    def ghost(self, game: "Game", registers: bool = False) -> bool:
        """Determine whether the player is (or registers as) dead."""
        return self.is_status(game, "dead", registers)

    def functioning(self, game: "Game", registers: bool = False) -> bool:
        """Determine whether the player is (or registers as) functioning."""
        return not self.is_status(game, "not_functioning", registers)

    def can_nominate(self, game: "Game") -> bool:
        """Determine whether the player can nominate."""
        return (
            not self.ghost(game, registers=True)
            or self.is_status(game, "can_nominate_while_dead")
        ) and (
            self.nominations_today == 0
            or (
                self.nominations_today == 1
                and self.is_status(game, "can_nominate_twice")
            )
        )

    # noinspection PyUnusedLocal
    # these args will be necessary for forwards compatibility ex for matron
    def can_be_nominated(self, game: "Game", nominator: "Player") -> bool:
        """Determine whether the player can be nominated."""
        return not self.has_been_nominated

    def can_vote(self, game: "Game", traveler: bool = False) -> bool:
        """Determine whether the player can vote."""
        if traveler:
            return True
        return (
            (not self.ghost(game, registers=True))
            or self.dead_votes > 0
            or self.is_status(game, "can_dead_vote_without_token")
        )

    def vote_value(self, game: "Game", traveler=False) -> int:
        """Determine the player's vote's value."""
        if traveler:
            return 1
        multiplier = 1
        if self.is_status(game, "thiefed"):
            multiplier *= -1
        if self.is_status(game, "bureaucrated"):
            multiplier *= -3
        return multiplier

    # Effect management
    def is_status(
        self, game: "Game", status_name: str, registers: bool = False
    ) -> bool:
        """Determine whether the player is affected by a status.

        Parameters
        ----------
        game : Game
            The current game.
        status_name : str
            The status.
        registers : bool
            Whether to check if they register as the status, or have the status.

        Returns
        -------
        bool
            Whether they have (or register as) the status.
        """
        try:
            if registers:
                for effect in self.effects:
                    if effect.registers_status(game, status_name):
                        return True

            for effect in self.effects:
                if effect.status(game, status_name):
                    return True

            return False

        except RecursionError:
            print(
                (
                    "Hit a recursion error while determining "
                    f"whether {self.nick} is {status_name}.",
                ),
            )
            traceback.print_exc()
            return True

    def exclusive_status_search(
        self, game: "Game", statuses: typing.List[str]
    ) -> typing.Optional[str]:
        """Determine which of a list of statuses applies to the player.

        This assumes that the statuses are mutually exclusive.

        Parameters
        ----------
        game : Game
            The current game.
        statuses : List[str]
            The statuses to check.

        Returns
        -------
        Optional[str]
            The matching status, or None.
        """
        for status in statuses:
            if self.is_status(game, status):
                return status
        return None

    def message_history_with(self, player: "Player") -> str:
        """Generate the player's message history with a player.

        Parameters
        ----------
        player
            The player to generate the message history with.

        Returns
        -------
        str
            The message history.
        """
        message_text = "__Message History__"
        message_text += f" (with {player.nick})"
        message_text += ":"
        previously_from: Optional[Player] = None
        for message in self.message_history:

            if player not in (message["from"], message["to"]):
                # don't process messages not part of the relevant history
                continue

            if previously_from != message["from"]:
                previously_from = message["from"]
                message_text += f'\n{message["from"].nick}:'

            message_text += f'\n> {message["content"]}'
        return message_text

    # Gameplay Methods
    def morning(self, inactive_role: Role):
        """Handle basic cleanup at the beginning of the day.

        Called by Game.startday.
        """
        if self.member in inactive_role.members:
            self.is_inactive = True
        else:
            self.is_inactive = False
        self.nominations_today = 0
        self.has_been_nominated = False
        self.has_spoken = self.is_inactive
        self.has_skipped = self.is_inactive

    async def message(self, ctx: "GameContext", frm: "Player"):
        """Handle inbound PMs to the player.

        Reports the message in public and saves the message to both player's histories.

        Parameters
        ----------
        ctx : GameContext
            The invocation context.
        frm : Player
            The PM's author.
        """
        content = await get_input(
            ctx, f"Messaging {self.nick}. What would you like to send?"
        )

        # messages to storytellers
        if self.is_status(ctx.bot.game, "storyteller"):
            for st in ctx.bot.game.storytellers:
                message = await safe_send(
                    st.member,
                    (
                        f"{st.member.mention}, message from {frm.nick} to "
                        f"storyteller {self.nick}: **{content}**"
                    ),
                )  # STs get the
                # bolded message for a message to any ST

            for observer in ctx.bot.observer_role.members:
                await safe_send(
                    observer, f"**[**{frm.nick} **>** {self.nick}**]** {content}",
                )

        # other messages
        else:
            message = await safe_send(
                self.member, f"Message from {frm.nick}: **{content}**",
            )

            # inform sts and observers
            for st in ctx.bot.game.storytellers:
                await safe_send(
                    st.member, f"**[**{frm.nick} **>** {self.nick}**]** {content}",
                )

            for observer in ctx.bot.observer_role.members:
                await safe_send(
                    observer, f"**[**{frm.nick} **>** {self.nick}**]** {content}",
                )

        # public report
        if ctx.bot.instant_message_reporting:
            await safe_send(ctx.bot.channel, f"**{frm.nick}** > **{self.nick}**")

        # update message histories
        # noinspection PyUnboundLocalVariable
        # think this is a false positive
        message_dict = {
            "from": frm,
            "to": self,
            "content": content,
            "day": ctx.bot.game.day_number,
            "time": message.created_at,
        }
        self.message_history.append(message_dict)
        frm.message_history.append(message_dict)

        # complete
        await frm.make_active(ctx.bot.game)
        await safe_send(frm.member, "Message sent!")
        return

    def revive(self, game: "Game") -> str:
        """Handle effect cleanup when the player revives.

        Parameters
        ----------
        game: Game
            The current game.

        Returns
        -------
        str
            A string reporting the revival.
        """
        effect_list = [x for x in self.effects]
        for effect in effect_list:
            if effect.status(game, "dead") or effect.status(game, "used_ability"):
                # TODO: figure out how this should work with registers_status
                self.effects.remove(effect)

        for effect in self.source_effects(game):
            effect.source_starts_functioning(game)

        return f"{self.nick} has come back to life."

    async def change_character(
        self, ctx: "GameContext", new_character: typing.Type["Character"]
    ):
        """Change the player's character. Handle effect cleanup."""
        effect_list = [x for x in self.source_effects(ctx.bot.game)]
        for effect in effect_list:
            if effect not in (Good, Evil):
                effect.delete(ctx.bot.game)

        self.character = new_character(self)
        for effect_type in self.character.default_effects:
            if effect_type not in (Good, Evil):
                self.add_effect(ctx.bot.game, effect_type, self)

        # TODO: this needs to be tested
        if self.character in ctx.bot.game.script.first_night:
            if ctx.bot.game.current_night:
                ctx.bot.game.current_night.add(self.character)

        await safe_send(
            ctx, f"Successfully changed {self.nick} to the {self.character.name}."
        )

    def add_effect(
        self, game: "Game", effect: typing.Type["Effect"], source_player: "Player"
    ) -> Effect:
        """Add non-default effects to the player.

        This is basically a factory method for an arbitrary Effect. It handles
        side-effects of the effect's initialization, for instance shutting down other
        effects. Except in the Player constructor, this should always be called instead
        of the Effect constructor.
        """
        effect_object = effect(self, source_player)

        def effect_adder():
            """Add the effect to the player's effects list."""
            self.effects.append(effect_object)

        return effect_object.turn_on(game, effect_adder)

    async def execute(self, ctx: "GameContext"):
        """Execute the player."""
        message_text = f"{self.nick} has been executed, "
        if self.ghost(ctx.bot.game):
            await safe_send(
                ctx.bot.channel, message_text + "but is already dead.",
            )

        elif self.is_status(ctx.bot.game, "safe"):
            await safe_send(
                ctx.bot.channel, message_text + "but does not die.",
            )

        else:
            await safe_send(ctx.bot.channel, message_text + "and dies.")
            self.add_effect(ctx.bot.game, Dead, self)

        # Day.end has a "successfully ended the day" message so this is above that
        if safe_bug_report(ctx):
            await safe_send(ctx, f"Successfully executed {self.nick}.")

        if ctx.bot.game.current_day:
            # TODO: currently doesn't support extra-nomination effects
            await ctx.bot.game.current_day.end(ctx)

    async def make_active(self, game: "Game"):
        """Set has_spoken to true and update storytellers."""

        def _updater_func(inner_game: "Game") -> typing.List["Player"]:
            if self.has_spoken:
                raise _UpdateUnnecessaryError
            self.has_spoken = True
            return inner_game.not_active

        await _update_activity(game, _updater_func, "spoken", "speak")

    async def add_nomination(self, ctx: "DayContext", skip: bool = False):
        """Set has_spoken to true and update storytellers."""

        def _updater_func(game: "Game") -> typing.List["Player"]:
            if skip:
                if not self.has_skipped:
                    self.has_skipped = True
                else:
                    raise commands.BadArgument("You have already skipped.")
            else:
                self.nominations_today += 1
            return game.to_nominate

        await _update_activity(
            ctx.bot.game, _updater_func, "nominated or skipped", "nominate or skip"
        )

    # Helpful properties
    @property
    def nick(self) -> str:
        """Determine the name the bot will call the player.

        Their nickname if set in preferences, else server nickname, else discord name.
        """
        return load_preferences(
            self.member
        ).nick  # the preferences object defaults to obj.nick =
        # member.display_name

    @property
    def epithet(self) -> str:
        """Determine a character epithet, ie "nick, the character"."""
        return f"{self.nick}, the {self.character.name}"

    def formatted_epithet(self, text: str) -> str:
        """Determine a character epithet, with text inserted before the character."""
        if text != "":
            return f"{self.nick}, the {text} {self.character.name}"
        return self.epithet

    @property
    def display_name(self) -> str:
        """Determine the player's server nickname if applicable, else discord name."""
        return self.member.display_name

    @property
    def name(self) -> str:
        """Determine the player's discord name."""
        return self.member.name

    @property
    def id(self) -> int:
        """Determine the player's discord id."""
        return self.member.id

    def __repr__(self):
        """Add easier formatting for repl introspection and debugging."""
        return self.epithet

    # Dill Stuff
    def __getstate__(self) -> dict:
        """Cleanup when pickled."""
        state = self.__dict__.copy()
        state["member"] = self.member.id  # discord snowflake objects are not picklable
        return state

    def __hash__(self):
        """Hashes the object."""
        try:
            return hash(self.member.id)
        except AttributeError:
            return hash(self.member)

    def __eq__(self, other) -> bool:
        """Compare two Player objects."""
        if isinstance(other, type(self)):
            try:
                return self.member.id == other.member.id
            except AttributeError:
                return self.member == self.member
        return NotImplemented
