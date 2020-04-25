"""Contains the storytelling cog, for commands related to storytelling."""

from os.path import isfile
from typing import List

from discord.ext import commands

from lib import checks
from lib.logic.Effect import Good, Evil, Dead
from lib.logic.Player import Player
from lib.logic.converters import to_script, to_character
from lib.logic.playerconverter import to_player, to_member
from lib.preferences import load_preferences
from lib.typings.context import Context

from lib.utils import (
    get_bool_input,
    safe_send,
    get_player,
    to_bool,
)


class Storytelling(commands.Cog):
    """Commands for storytelling."""

    # TODO: separate these into multiple cogs

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.is_not_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def startgame(self, ctx: Context, *, script: str):
        """Start the game.

        script: The game's script. Available scripts can be viewed with `script list`.

        You'll be asked for two pieces of input:

        First, the seating order:
        This is a line-separated, ordered list of the game's players.
        Do not include travelers.

        Second, the characters:
        This is a line-separated, ordered list of the corresponding characters.
        """
        await ctx.bot.start_game(ctx, to_script(ctx, script))
        await safe_send(ctx, "Started the game successfully.")

    @commands.command()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def endgame(self, ctx: Context, winner: str):
        """End the game.

        winner: 'good' or 'evil'. Can be 'neutral' in the event of a rerack.

        This command often takes a long time, as it unpins a large number of messages.
        """
        with ctx.typing():

            # verify valid winner
            winner = winner.lower()
            if winner not in ["good", "evil", "neutral"]:
                raise commands.BadArgument(
                    "The winner must be 'good,' 'evil,' or 'neutral,' exactly."
                )

            # set winner
            ctx.bot.game.winner = winner

            # endgame message
            if winner != "neutral":
                await safe_send(
                    ctx.bot.channel,
                    f"{ctx.bot.player_role.mention}, {winner} has won. Good game!",
                )
            else:
                await safe_send(
                    ctx.bot.channel,
                    f"{ctx.bot.player_role.mention}, the game is being remade.",
                )

            # unpin messages
            # TODO: unpin the script messages as well
            for msg in await ctx.bot.channel.pins():
                if msg.created_at >= ctx.bot.game.seating_order_message.created_at:
                    await msg.unpin()

            # backup
            i = 1
            while isfile(f"{ctx.bot.bot_name}/old/game_{i}.pckl"):
                i += 1
            ctx.bot.backup(f"old/game_{i}.pckl")

            # thank storytellers
            for st in ctx.bot.game.storytellers:
                await safe_send(
                    st.member, "Thank you for storytelling! We appreciate you <3"
                )

            # delete game
            ctx.bot.game = None

            # complete
            await safe_send(ctx, "Ended the game successfully.")
            return

    @commands.command()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def addtraveler(
        self,
        ctx: Context,
        traveler: str,
        upwards_neighbor: str,
        alignment: str,
        *,
        character: str,
    ):
        """Add a traveler to the game.

        traveler: The player to join the game.
        character: Their traveler character.
        upwards_neighbor: The player above them in the seating order.
        alignment: The traveler's alignment; 'good' or 'evil'.
        """
        # convert the traveler
        traveler_actual = await to_member(ctx, traveler)

        # check alignment is valid
        if not alignment.lower() in ["good", "evil"]:
            raise commands.BadArgument(
                "The alignment must be 'good' or 'evil' exactly."
            )

        # check if person is in the game
        try:
            get_player(ctx.bot.game, traveler_actual.id)
            raise commands.BadArgument(
                f"{load_preferences(traveler_actual).nick} is already in the game."
            )

        except ValueError as e:

            if str(e) == "player not found":

                # find the character
                character_actual = to_character(ctx, character)

                # determine the position
                upwards_neighbor_actual = await to_player(ctx, upwards_neighbor)

                # make the Player
                player = Player(
                    traveler_actual,
                    character_actual,
                    upwards_neighbor_actual.position + 1,
                )

                # check that the character is a traveler
                if not player.character_type(ctx) == "traveler":
                    raise commands.BadArgument(
                        f"{player.character.name} is not a traveler."
                    )

                # add the alignment
                if alignment.lower() == "good":
                    player.effects.append(Good(ctx, player, player))
                elif alignment.lower() == "evil":
                    player.effects.append(Evil(ctx, player, player))

                # add the player role
                await traveler_actual.add_roles(ctx.bot.player_role)

                # add them to the seating order
                ctx.bot.game.seating_order.insert(
                    upwards_neighbor_actual.position + 1, player
                )

                # announcement
                await safe_send(
                    ctx.bot.channel,
                    (
                        "{townsfolk}, {player} has joined the town as the {traveler}. "
                        "Let's tell {pronoun} hello!"
                    ).format(
                        traveler=player.character.name,
                        pronoun=load_preferences(player).pronouns[1],
                        townsfolk=ctx.bot.player_role.mention,
                        player=player.nick,
                    ),
                )

                # rules
                msg = await safe_send(
                    ctx.bot.channel,
                    f"\n**{player.character.name}** - {player.character.rules_text}",
                )
                await msg.pin()
                await safe_send(
                    ctx,
                    f"Successfully added {player.nick} as the {player.character.name}.",
                )

            else:
                raise

    @commands.command()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def removetraveler(self, ctx: Context, traveler: str):
        """Remove a traveler from the game.

        traveler: The traveler to remove.
        """
        # convert the traveler
        traveler_actual = await to_player(ctx, traveler)

        # check that player is a traveler
        if not traveler_actual.character_type(ctx) == "traveler":
            raise commands.BadArgument(f"{traveler_actual.nick} is not a traveler.")

        # remove them from the seating order
        ctx.bot.game.seating_order.remove(traveler_actual)

        # announcement
        msg = await safe_send(
            ctx.bot.channel,
            (
                "{townsfolk}, {traveler} has left the town. "
                "Let's wish {pronoun} goodbye!"
            ).format(
                pronoun=load_preferences(traveler_actual).pronouns[1],
                townsfolk=ctx.bot.player_role.mention,
                traveler=traveler_actual.nick,
            ),
        )
        await msg.pin()
        await safe_send(ctx, f"Successfully removed traveler {traveler_actual.nick}.")

    @commands.command()
    @checks.is_day()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def endday(self, ctx: Context):
        """End the current day."""
        # confirm
        if not await get_bool_input(
            ctx,
            (
                "This will end the day without executing. "
                "To end the day via execution, the `execute` command. "
                "Do you want to continue?"
            ),
        ):
            await safe_send(ctx, "Cancelled.")
            return

        await safe_send(ctx.bot.channel, "No one was executed.")
        await ctx.bot.game.current_day.end(ctx)

    @commands.group()
    @checks.is_night()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def startday(self, ctx):
        """Start the day.

        This will perform the action of most characters in the night order.
        It does not handle info roles or other roles with no effect on the gamestate.
        """
        return await ctx.bot.game.startday(ctx)

    @startday.command()
    async def arbitrarykills(self, ctx: Context, *, kills: str):
        """Start the day with arbitrary additional kills at the beginning of the night.

        kills: Any players to kill.
        This goes through protection, but cannot kill dead players.
        The players are killed at the beginning of the night.
        """
        kills_actual = []  # type: List[Player]
        # convert kills
        for kill_string in kills:
            kills_actual.append(await to_player(ctx, kill_string))

        for player in kills_actual:
            if not player.ghost(ctx):
                player.effects.append(Dead(ctx, player, player))

        await ctx.bot.game.startday(ctx, kills_actual)

    @commands.command(name="open")
    @checks.is_day()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def _open(self, ctx: Context):
        """Open PMs and nominations."""
        await ctx.bot.game.current_day.open_pms(ctx)
        await ctx.bot.game.current_day.open_noms(ctx)

    @commands.command()
    @checks.is_day()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def opennoms(self, ctx: Context):
        """Open nominations."""
        await ctx.bot.game.current_day.open_noms(ctx)

    @commands.command()
    @checks.is_day()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def openpms(self, ctx: Context):
        """Open PMs."""
        await ctx.bot.game.current_day.open_pms(ctx)

    @commands.command(name="close")
    @checks.is_day()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def _close(self, ctx: Context):
        """Close PMs and nominations."""
        await ctx.bot.game.current_day.close_pms(ctx)
        await ctx.bot.game.current_day.close_noms(ctx)

    @commands.command()
    @checks.is_day()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def closenoms(self, ctx: Context):
        """Close nominations."""
        await ctx.bot.game.current_day.close_noms(ctx)

    @commands.command()
    @checks.is_day()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def closepms(self, ctx: Context):
        """Close PMs."""
        await ctx.bot.game.current_day.close_pms(ctx)

    @commands.command()
    @checks.is_not_vote()
    @checks.noms_open()
    @checks.is_day()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def stnominate(self, ctx: Context, nominee: str):
        """Nominate a player for execution.

        nominee: The player to nominate.

        If you want to simulate a nomination by a player, use proxynominate.
        """
        await ctx.bot.game.current_day.nominate(
            ctx, nominee, get_player(ctx.bot.game, ctx.message.author.id)
        )
        await safe_send(ctx, f"Successfully nominated.")

    @commands.command()
    @checks.is_not_vote()
    @checks.noms_open()
    @checks.is_day()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def proxynominate(self, ctx: Context, nominee: str, nominator: str):
        """Simulate a nomination by a player.

        nominee: The player to nominate.
        nominator: The player who performed the nomination.

        This is used to simulate nominations by players, primarily for troubleshooting.
        If you want to nominate without a nominator, use stnominate.
        """
        nominator_actual = await to_player(ctx, nominator)
        try:
            await ctx.bot.game.current_day.nominate(ctx, nominee, nominator_actual)
            await safe_send(ctx, f"Successfully nominated for {nominator_actual.nick}.")
        except ValueError as e:
            if str(e) == "nominator already nominated":
                return await safe_send(
                    ctx, f"{nominator_actual.nick} cannot nominate today."
                )
            raise

    @commands.command()
    @checks.is_vote()
    @checks.is_day()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def proxyvote(self, ctx, voter: str, vote: str):
        """Simulate a vote by a player.

        voter: The player to vote for.
        vote: The vote to input.
        """
        voter_actual = await to_player(ctx, voter)
        vote_actual = to_bool(vote)
        if ctx.bot.game.current_day.current_vote.to_vote != voter_actual:
            await safe_send(
                ctx,
                "It is not {player}'s vote. It is {actual_voter}'s vote.".format(
                    actual_voter=ctx.bot.game.current_day.current_vote.to_vote.nick,
                    player=voter_actual.nick,
                ),
            )
        await ctx.bot.game.current_day.current_vote.vote(ctx, voter_actual, vote_actual)
        await safe_send(ctx, f"Successfully voted for {voter_actual.nick}.")

    @commands.command()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def execute(self, ctx: Context, player: str):
        """Execute a player.

        player: The player to be executed.

        This will end the day, and kill the player, as appropriate.
        """
        player_actual = await to_player(ctx, player)
        await player_actual.execute(ctx)

    @commands.command()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def exile(self, ctx: Context, traveler: str):
        """Exile a traveler.

        traveler: The traveler to be executed.

        This will kill the player, as appropriate.
        """
        traveler_actual = await to_player(ctx, traveler)
        if not traveler_actual.character_type(ctx) == "traveler":
            await safe_send(
                ctx.bot.channel, f"{traveler_actual.nick} is not a traveler.",
            )
            return

        await traveler_actual.character.exile(ctx)
        await safe_send(ctx, f"Successfully exiled {traveler_actual.nick}.")

    @commands.command()
    @checks.is_game()
    @checks.is_storyteller()
    @checks.is_dm()
    async def revive(self, ctx: Context, player: str):
        """Revive a player.

        player: The player to be revived.
        """
        player_actual = await to_player(ctx, player)
        msg = await safe_send(ctx.bot.channel, await player_actual.revive(ctx))
        await msg.pin()
        await safe_send(ctx, f"Successfully revived {player_actual.nick}.")


def setup(bot):
    """Set the cog up."""
    bot.add_cog(Storytelling(bot))
