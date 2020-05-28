from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

import discord
from discord.ext import commands

from lib.bot import BOTCBot

_C = TypeVar("_C", bound=Context)
_T = TypeVar("_T",)

class Context(commands.Context):
    message: discord.Message
    bot: BOTCBot
    args: List[Any]
    kwargs: Dict[str, Any]
    prefix: str
    command: commands.Command[Any]
    invoked_with: Optional[str]
    invoked_subcommand: Optional[commands.Command[Any]]
    subcommand_passed: Optional[str]
    command_failed: bool
    async def invoke(
        self, __command: Command[_C], *args: Any, **kwargs: Any
    ) -> Any: ...
    async def reinvoke(
        self, *, call_hooks: bool = ..., restart: bool = ...
    ) -> None: ...
    @property
    def valid(self) -> bool: ...
    @property
    def cog(self: _C) -> Optional[Cog[_C]]: ...
    @cached_property
    def guild(self) -> Optional[discord.Guild]: ...
    @cached_property
    def channel(
        self,
    ) -> Union[discord.TextChannel, discord.DMChannel, discord.GroupChannel]: ...
    @cached_property
    def author(self) -> Union[discord.User, discord.Member]: ...
    @cached_property
    def me(self) -> Union[discord.Member, discord.ClientUser]: ...
    @property
    def voice_client(self) -> Optional[discord.VoiceClient]: ...
    async def send_help(
        self: _C, __entity: Optional[Union[Command[_C], Cog[_C], str]]
    ) -> Any: ...

class _BotWithGame(BOTCBot):
    game: Game

class _GameWithDay(Game):
    current_day: Day
    current_night: None

class _GameWithNight(Game):
    current_night: Night
    current_day: None

class _DayWithVote(Day):
    current_vote: Vote

class _GameWithVote(_GameWithDay):
    current_day: _DayWithVote

class _BotWithDay(_BotWithGame):
    game: _GameWithDay

class _BotWithNight(_BotWithGame):
    game: _GameWithNight

class _BotWithVote(_BotWithDay):
    game: _GameWithVote

class GameContext(Context):
    bot: _BotWithGame

class DayContext(GameContext):
    bot: _BotWithDay

class NightContext(GameContext):
    bot: _BotWithNight

class VoteContext(DayContext):
    bot: _BotWithVote
