"""Contains the GameManagement cog, for commands related to game management."""

from discord.ext import commands

from lib import checks
from lib.logic.Effect import Good, Evil
from lib.logic.Player import Player
from lib.logic.converters import to_character
from lib.logic.playerconverter import to_player, to_member
from lib.preferences import load_preferences
from lib.typings.context import Context
from lib.utils import (
    safe_send,
    get_player,
    to_bool,
)


class GameManagement(commands.Cog, name="Game Management"):
    """Commands for game management."""

    def __init__(self, bot):
        self.bot = bot

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
                if not player.is_status(ctx.bot.game, "traveler"):
                    raise commands.BadArgument(
                        f"{player.character.name} is not a traveler."
                    )

                # add the alignment
                if alignment.lower() == "good":
                    player.add_effect(ctx.bot.game, Good, player)
                elif alignment.lower() == "evil":
                    player.add_effect(ctx.bot.game, Evil, player)

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
        if not traveler_actual.is_status(ctx.bot.game, "traveler"):
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
        vote_actual = to_bool(vote, "vote")
        if ctx.bot.game.current_day.current_vote.to_vote != voter_actual:
            await safe_send(
                ctx,
                "It is not {player}'s vote. It is {actual_voter}'s vote.".format(
                    actual_voter=ctx.bot.game.current_day.current_vote.to_vote.nick,
                    player=voter_actual.nick,
                ),
            )
            return
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
        if not traveler_actual.is_status(ctx.bot.game, "traveler"):
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
        msg = await safe_send(ctx.bot.channel, player_actual.revive(ctx.bot.game))
        await msg.pin()
        await safe_send(ctx, f"Successfully revived {player_actual.nick}.")


def setup(bot):
    """Set the cog up."""
    bot.add_cog(GameManagement(bot))
