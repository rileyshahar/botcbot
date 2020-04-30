"""Contains the BOTCBot class."""

import typing
from os import remove
from os.path import isfile

import discord
from dill import dump, load
from discord.ext import commands

from lib.logic.Character import Storyteller
from lib.logic.Game import Game
from lib.logic.Player import Player
from lib.logic.converters import to_character_list
from lib.logic.playerconverter import to_member_list
from lib.logic.tools import generate_game_info_message
from lib.preferences import load_preferences
from lib.utils import safe_send, get_input

if typing.TYPE_CHECKING:
    from lib.logic.Script import Script
    from lib.typings.context import Context
    from configparser import SectionProxy


class BOTCBot(commands.Bot):
    """An extension of the commands.Bot class, storing globally necessary attributes."""

    def __init__(
        self,
        bot_name: str,
        serverid: int,
        channelid: int,
        storytellerid: int,
        playerid: int,
        inactiveid: int,
        playtestid: int,
        observerid: int,
        config: "SectionProxy",
        **options,
    ):
        super().__init__(**options)

        self.bot_name = bot_name
        self._serverid = serverid
        self._channelid = channelid
        self._storytellerid = storytellerid
        self._playerid = playerid
        self._inactiveid = inactiveid
        self._playtestid = playtestid
        self._observerid = observerid
        self.config = config
        self.game: typing.Optional[Game] = None

    @property
    def server(self) -> discord.Guild:
        """Determine the bot's main server."""
        return self.get_guild(self._serverid)

    @property
    def channel(self) -> discord.TextChannel:
        """Determine the bot's main channel."""
        return self.get_channel(self._channelid)

    @property
    def storyteller_role(self) -> discord.Role:
        """Determine the bot's Storyteller role."""
        return self.server.get_role(self._storytellerid)

    @property
    def player_role(self) -> discord.Role:
        """Determine the bot's player role."""
        return self.server.get_role(self._playerid)

    @property
    def inactive_role(self) -> discord.Role:
        """Determine the bot's inactive role."""
        return self.server.get_role(self._inactiveid)

    @property
    def playtest_role(self) -> typing.Optional[discord.Role]:
        """Determine the bot's playtest role."""
        if self.playtest:
            return self.server.get_role(self._playtestid)
        return None

    @property
    def observer_role(self) -> discord.Role:
        """Determine the bot's observer role."""
        return self.server.get_role(self._observerid)

    @property
    def instant_message_reporting(self) -> bool:
        """Determine whether the bot uses instant message reporting."""
        return self.config.getboolean("instantmessagereports")
        # TODO: this isnt working

    @property
    def playtest(self) -> bool:
        """Determine whether the bot has playtest characters enabled."""
        return self.config.getboolean("playtest")

    async def start_game(self, ctx: "Context", script: "Script"):
        """Handle startgame logic."""
        await safe_send(ctx, f"Starting a {script.name} game.")

        # ask for the list of players
        users = await to_member_list(
            ctx,
            (
                await get_input(
                    ctx,
                    (
                        "What is the seating order? (Separate "
                        "users with line breaks. Do not include "
                        "travelers.)"
                    ),
                )
            ).split("\n"),
        )

        # ask for the list of characters
        characters = to_character_list(
            ctx,
            (
                await get_input(
                    ctx,
                    (
                        "What are the corresponding characters? "
                        "(Separate characters with line breaks.)"
                    ),
                )
            ).split("\n"),
            script,
        )

        with ctx.typing():  # doing a lot of computation here

            # verify 1:1 user:character ratio
            if len(users) != len(characters):
                raise commands.BadArgument(
                    "There are a different number of players and characters."
                )

            # role cleanup
            await self._startgame_role_cleanup(users)

            # generate seating order
            seating_order = [
                Player(person, characters[index], index)
                for index, person in enumerate(users)
            ]

            # script message
            posts = []
            for content in list(script.info(ctx)):
                posts.append(await safe_send(self.channel, content))

            for post in posts[::-1]:  # Reverse the order so the pins are right
                await post.pin()

            # welcome message
            await safe_send(
                self.channel,
                (
                    f"{self.player_role.mention}, "
                    "welcome to Blood on the Clocktower! Go to "
                    "sleep."
                ),
            )

            # Seating order message
            seating_order_message = await safe_send(
                self.channel, generate_game_info_message(seating_order, ctx),
            )
            await seating_order_message.pin()

            # storytellers
            storytellers = [
                Player(person, Storyteller, None)
                for person in self.storyteller_role.members
            ]

            # start the game
            self.game = Game(seating_order, seating_order_message, script, storytellers)

            # complete
            return

    async def update_status(self):
        """Update the bot's status to display information about the game."""
        if not self.game:
            await self.change_presence(
                status=discord.Status.dnd,
                activity=discord.Game(name="No ongoing game!"),
            )

        elif not self.game.current_day:
            await self.change_presence(
                status=discord.Status.idle,
                activity=discord.Game(name="It's nighttime!"),
            )

        else:
            clopen = ["Closed", "Open"]
            await self.change_presence(
                status=discord.Status.online,
                activity=discord.Game(
                    name="PMs {is_pms}, "
                    "Noms "
                    "{is_noms}!".format(
                        is_pms=clopen[self.game.current_day.is_pms],
                        is_noms=clopen[self.game.current_day.is_noms],
                    )
                    # noms instead of nominations for space
                ),
            )

    def backup(self, file_name: str = "current_game.pckl"):
        """Backs up the current gamestate."""
        file_name = "resources/backup/" + self.bot_name + "/" + file_name

        if self.game:
            with open(file_name, "wb") as file:
                dump(self.game, file)
        else:
            if isfile(file_name):
                remove(file_name)

    async def restore_backup(self, file_name: str = "current_game.pckl", mute=False):
        """Restores a backup."""
        file_name = "resources/backup/" + self.bot_name + "/" + file_name

        # restore backups
        try:

            with open(file_name, "rb") as file:
                self.game = load(file)

            # catch game being none
            # should never be possible if the file exists, but just in case
            assert self.game

            # do some unpickling
            # noinspection PyTypeChecker
            # the seating order message is pickled as an int so this is fine
            self.game.seating_order_message = await self.channel.fetch_message(
                self.game.seating_order_message
            )
            for player in self.game.seating_order + self.game.storytellers:
                player.member = self.server.get_member(player.member)

            # print
            if not mute:
                print("Backup restored!")
            return True

        except (FileNotFoundError, AssertionError):
            self.game = None
            if not mute:
                print("No backup found.")
            return None

        except EOFError:
            self.game = None
            print("Backup incomplete.")  # do this even if mute because it
            # represents an error
            return None

    async def process_commands(self, message: discord.Message):
        """Process commands registered to the bot.

        Modified to handle custom aliases.
        """
        if message.author.bot:
            return

        if not (message.guild is None or message.channel == self.channel):
            return

        ctx = await self.get_context(message)

        preferences = load_preferences(message.author)
        if ctx.invoked_with in preferences.aliases:
            ctx.command = self.all_commands.get(
                preferences.aliases[ctx.invoked_with].split(" ")[0]
            )
            if " " in preferences.aliases[ctx.invoked_with]:
                for cmd in preferences.aliases[ctx.invoked_with].split(" ")[1:]:
                    ctx.command = ctx.command.get_command(cmd)

        await self.invoke(ctx)

    async def _startgame_role_cleanup(self, users: typing.List[discord.Member]):
        """Handle role cleanup for startgame."""
        # clear all player roles
        for memb in self.player_role.members:
            await memb.remove_roles(self.player_role)

        # modify roles for players
        for user in users:

            # add player role
            await user.add_roles(self.player_role)

            # remove storyteller role
            if self.storyteller_role in user.roles:
                await user.remove_roles(self.storyteller_role)

        # add player role for storytellers
        for memb in self.storyteller_role.members:
            await memb.add_roles(self.player_role)
