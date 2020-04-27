"""Contains helpers for testing discord.py objects.

Adapted from https://github.com/python-discord/bot/blob/master/tests/helpers.py.
"""

# TODO: we should really only need to be mocking bots
# everything else should have a script to generate the actual object
# with sensible default values

import collections
import itertools
import unittest.mock
from typing import Iterable, Optional

import discord
from discord.ext.commands import Context

from lib.bot import BOTCBot
from lib.logic.Character import Character
from lib.logic.Player import Player
from lib.logic.Game import Game
from lib.logic.Script import Script
from lib.logic.Vote import Vote
from lib.logic.Day import Day


class HashableMixin(discord.mixins.EqualityComparable):
    """Provides similar hashing functionality as discord.py's `Hashable` mixin."""

    def __hash__(self):
        return self.id


class ColourMixin:
    """Provides the aliasing of color->colour like discord.py does."""

    @property
    def color(self) -> discord.Colour:
        return self.colour

    @color.setter
    def color(self, color: discord.Colour) -> None:
        self.colour = color


class CustomMockMixin:
    """Provides common functionality for our custom Mock types."""

    child_mock_type = unittest.mock.MagicMock
    discord_id = itertools.count(0)
    spec_set = None
    additional_spec_asyncs = None

    def __init__(self, **kwargs):
        name = kwargs.pop(
            "name", None
        )  # `name` has special meaning for Mock classes, so we need to set it manually.
        super().__init__(spec_set=self.spec_set, **kwargs)

        if self.additional_spec_asyncs:
            self._spec_asyncs.extend(self.additional_spec_asyncs)

        if name:
            self.name = name

    def _get_child_mock(self, **kw):
        """Stop the propagation of our custom mock classes."""
        _new_name = kw.get("_new_name")
        if _new_name in self.__dict__["_spec_asyncs"]:
            return unittest.mock.AsyncMock(**kw)

        _type = type(self)
        if (
            issubclass(_type, unittest.mock.MagicMock)
            and _new_name in unittest.mock._async_method_magics
        ):
            # Any asynchronous magic becomes an AsyncMock
            klass = unittest.mock.AsyncMock
        else:
            klass = self.child_mock_type

        if self._mock_sealed:
            attribute = "." + kw["name"] if "name" in kw else "()"
            mock_name = self._extract_mock_name() + attribute
            raise AttributeError(mock_name)

        return klass(**kw)


# Create a guild instance to get a realistic Mock of `discord.Guild`
guild_data = {
    "id": 1,
    "name": "guild",
    "region": "Europe",
    "verification_level": 2,
    "default_notications": 1,
    "afk_timeout": 100,
    "icon": "icon.png",
    "banner": "banner.png",
    "mfa_level": 1,
    "splash": "splash.png",
    "system_channel_id": 464033278631084042,
    "description": "mocking is fun",
    "max_presences": 10_000,
    "max_members": 100_000,
    "preferred_locale": "UTC",
    "owner_id": 1,
    "afk_channel_id": 464033278631084042,
}
guild_instance = discord.Guild(data=guild_data, state=unittest.mock.MagicMock())


# Create a Role instance to get a realistic Mock of `discord.Role`
role_data = {"name": "role", "id": 1}
role_instance = discord.Role(
    guild=guild_instance, state=unittest.mock.MagicMock(), data=role_data
)


class MockRole(CustomMockMixin, unittest.mock.Mock, ColourMixin, HashableMixin):
    """A Mock subclass to mock `discord.Role` objects."""

    spec_set = role_instance

    def __init__(self, **kwargs) -> None:
        default_kwargs = {
            "id": next(self.discord_id),
            "name": "role",
            "position": 1,
            "colour": discord.Colour(0xDEADBF),
            "permissions": discord.Permissions(),
        }
        super().__init__(**collections.ChainMap(kwargs, default_kwargs))

        if isinstance(self.colour, int):
            self.colour = discord.Colour(self.colour)

        if isinstance(self.permissions, int):
            self.permissions = discord.Permissions(self.permissions)

        if "mention" not in kwargs:
            self.mention = f"&{self.name}"

    def __lt__(self, other):
        """Simplified position-based comparisons similar to those of `discord.Role`."""
        return self.position < other.position


class MockGuild(CustomMockMixin, unittest.mock.Mock, HashableMixin):
    """A `Mock` subclass to mock `discord.Guild` objects."""

    spec_set = guild_instance

    def __init__(self, roles: Optional[Iterable[MockRole]] = None, **kwargs) -> None:
        default_kwargs = {"id": next(self.discord_id), "members": []}
        super().__init__(**collections.ChainMap(kwargs, default_kwargs))

        self.roles = [MockRole(name="@everyone", position=1, id=0)]
        if roles:
            self.roles.extend(roles)


# Create a Member instance to get a realistic Mock of `discord.Member`
member_data = {"user": "lemon", "roles": [1]}
state_mock = unittest.mock.MagicMock()
member_instance = discord.Member(
    data=member_data, guild=guild_instance, state=state_mock
)


class MockMember(CustomMockMixin, unittest.mock.Mock, ColourMixin, HashableMixin):
    """A Mock subclass to mock Member objects."""

    spec_set = member_instance

    def __init__(self, roles: Optional[Iterable[MockRole]] = None, **kwargs) -> None:
        default_kwargs = {"name": "member", "id": next(self.discord_id), "bot": False}
        super().__init__(**collections.ChainMap(kwargs, default_kwargs))

        self.roles = [MockRole(name="@everyone", position=1, id=0)]
        if roles:
            self.roles.extend(roles)

        if "mention" not in kwargs:
            self.mention = f"@{self.name}"


# Create a User instance to get a realistic Mock of `discord.User`
user_instance = discord.User(
    data=unittest.mock.MagicMock(), state=unittest.mock.MagicMock()
)


class MockUser(CustomMockMixin, unittest.mock.Mock, ColourMixin, HashableMixin):
    """A Mock subclass to mock User objects."""

    spec_set = user_instance

    def __init__(self, **kwargs) -> None:
        default_kwargs = {"name": "user", "id": next(self.discord_id), "bot": False}
        super().__init__(**collections.ChainMap(kwargs, default_kwargs))

        if "mention" not in kwargs:
            self.mention = f"@{self.name}"


# Create a TextChannel instance to get a realistic MagicMock of `discord.TextChannel`
channel_data = {
    "id": 1,
    "type": "TextChannel",
    "name": "channel",
    "parent_id": 1234567890,
    "topic": "topic",
    "position": 1,
    "nsfw": False,
    "last_message_id": 1,
}
state = unittest.mock.MagicMock()
guild = unittest.mock.MagicMock()
channel_instance = discord.TextChannel(state=state, guild=guild, data=channel_data)


class MockTextChannel(CustomMockMixin, unittest.mock.Mock, HashableMixin):
    """
    A MagicMock subclass to mock TextChannel objects.
    Instances of this class will follow the specifications of `discord.TextChannel` instances. For
    more information, see the `MockGuild` docstring.
    """

    spec_set = channel_instance

    def __init__(self, name: str = "channel", channel_id: int = 1, **kwargs) -> None:
        default_kwargs = {
            "id": next(self.discord_id),
            "name": "channel",
            "guild": MockGuild(),
        }
        super().__init__(**collections.ChainMap(kwargs, default_kwargs))

        if "mention" not in kwargs:
            self.mention = f"#{self.name}"


# Create a Message instance to get a realistic MagicMock of `discord.Message`
message_data = {
    "id": 1,
    "webhook_id": 431341013479718912,
    "attachments": [],
    "embeds": [],
    "application": "Python Discord",
    "activity": "mocking",
    "channel": unittest.mock.MagicMock(),
    "edited_timestamp": "2019-10-14T15:33:48+00:00",
    "type": "message",
    "pinned": False,
    "mention_everyone": False,
    "tts": None,
    "content": "content",
    "nonce": None,
}

message_instance = discord.Message(
    state=unittest.mock.MagicMock(),
    channel=unittest.mock.MagicMock(),
    data=message_data,
)


class MockMessage(CustomMockMixin, unittest.mock.MagicMock):
    """
    A MagicMock subclass to mock Message objects.
    Instances of this class will follow the specifications of `discord.Message` instances. For more
    information, see the `MockGuild` docstring.
    """

    spec_set = message_instance

    def __init__(self, **kwargs) -> None:
        default_kwargs = {"attachments": []}
        super().__init__(**collections.ChainMap(kwargs, default_kwargs))
        self.author = kwargs.get("author", MockMember())
        self.channel = kwargs.get("channel", MockTextChannel())


player_instance = Player(MockMember(), Character, 0)


class MockPlayer(CustomMockMixin, unittest.mock.MagicMock):
    spec_set = player_instance

    def __init__(self, **kwargs) -> None:
        default_kwargs = {
            "member": MockMember(),
            "character": Character(self),
            "position": 1,
            "effects": [],
            "dead_votes": 1,
            "message_history": [],
            "has_spoken": False,
            "nominations_today": 0,
            "has_been_nominated": False,
            "has_skipped": False,
            "is_inactive": False,
        }
        super().__init__(**collections.ChainMap(kwargs, default_kwargs))

    def __getstate__(self) -> dict:
        """Cleanup when pickled."""
        state = self.__dict__.copy()
        state["member"] = self.member.id  # discord snowflake objects are not picklable
        return state

    def __hash__(self):
        """Hashes the object."""
        return hash(self.member.id)

    def __eq__(self, other) -> bool:
        """Compare two Player objects."""
        if isinstance(other, type(self)):
            try:
                return self.member.id == other.member.id
            except AttributeError:
                return self.member == self.member
        return NotImplemented


script_instance = Script(
    "Mock Script", [Character], first_night=[Character], other_nights=[Character]
)


class MockScript(CustomMockMixin, unittest.mock.MagicMock):
    spec_set = script_instance

    def __init__(self, **kwargs) -> None:
        default_kwargs = {
            "name": "Mock Script",
            "character_list": [Character],
            "aliases": [],
            "editors": [],
            "playtest": False,
            "first_night": [Character],
            "other_nights": [Character],
        }
        super().__init__(**collections.ChainMap(kwargs, default_kwargs))


game_instance = Game(
    [MockPlayer()], MockMessage(), MockScript(), [MockPlayer(position=None)]
)


class MockGame(CustomMockMixin, unittest.mock.MagicMock):
    def __init__(self, **kwargs) -> None:
        default_kwargs = {
            "name": "Mock Script",
            "past_days": [],
            "current_day": None,
            "seating_order": [MockPlayer()],
            "seating_order_message": MockMessage(),
            "script": MockScript(),
            "storytellers": [MockPlayer(position=None)],
        }
        super().__init__(**collections.ChainMap(kwargs, default_kwargs))


bot_instance = BOTCBot(
    "Mock Bot",
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    unittest.mock.MagicMock(return_value=False),
    command_prefix=unittest.mock.MagicMock(),
)


class MockBOTCBot(CustomMockMixin, unittest.mock.MagicMock):

    spec_set = bot_instance
    additional_spec_asyncs = ("wait_for",)

    def __init__(self, **kwargs) -> None:
        default_kwargs = {
            "bot_name": "Mock Bot",
            "_serverid": next(self.discord_id),
            "_channelid": next(self.discord_id),
            "_storytellerid": next(self.discord_id),
            "_playerid": next(self.discord_id),
            "_inactiveid": next(self.discord_id),
            "_playtestid": next(self.discord_id),
            "_observerid": next(self.discord_id),
            "game": MockGame(),
            "command_prefix": ("@", ","),
        }
        super().__init__(**collections.ChainMap(kwargs, default_kwargs))
        self.loop.create_task.side_effect = lambda coroutine: coroutine.close()

    @property
    def instant_message_reporting(self) -> bool:
        """Determine whether the bot uses instant message reporting."""
        return False

    @property
    def playtest(self) -> bool:
        """Determine whether the bot has playtest characters enabled."""
        return True


# Create a Context instance to get a realistic MagicMock of `discord.ext.commands.Context`
context_instance = Context(
    message=unittest.mock.MagicMock(), prefix=unittest.mock.MagicMock()
)


class MockContext(CustomMockMixin, unittest.mock.MagicMock):
    """
    A MagicMock subclass to mock Context objects.
    Instances of this class will follow the specifications of `discord.ext.commands.Context`
    instances. For more information, see the `MockGuild` docstring.
    """

    spec_set = context_instance

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.bot = kwargs.get("bot", MockBOTCBot())
        self.guild = kwargs.get("guild", MockGuild())
        self.author = kwargs.get("author", MockMember())
        self.channel = kwargs.get("channel", MockTextChannel())
