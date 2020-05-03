"""Contains the PreferenceManagement cog for commands relating to preferences."""

from discord.ext import commands

from lib import checks
from lib.bot import BOTCBot
from lib.preferences import load_preferences
from lib.typings.context import Context
from lib.utils import safe_send, to_bool


class PreferenceManagement(commands.Cog, name="[General] Preferences"):
    """Commands for preference management.

    Note that preferences are generally global (stored across all BOTC bots).
    """

    def __init__(self, bot: BOTCBot):
        self.bot = bot

    @commands.command()
    @checks.is_dm()
    async def makealias(
        self, ctx: Context, alias: str, command: str, *, subcommand: str = ""
    ):
        """Create a personal alias for a command.

        alias: The alias to be created.
        command: The command to create the alias for.
        """
        preferences = load_preferences(ctx.message.author)
        cmd = ctx.bot.all_commands.get(command)
        if cmd is None:
            await safe_send(
                ctx,
                "Command not found: {command}.".format(
                    command=command + (" " if subcommand else "") + subcommand
                ),
            )
        elif subcommand:
            if cmd.get_command(subcommand) is None:
                await safe_send(
                    ctx,
                    "Command not found: {command}.".format(
                        command=command + " " + subcommand
                    ),
                )
        else:
            preferences.aliases[alias] = (
                command + (" " if subcommand else "") + subcommand
            )
            preferences.save_preferences()
            await safe_send(
                ctx,
                "Successfully created alias `{alias}` for command `{command}`.".format(
                    alias=alias, command=preferences.aliases[alias]
                ),
            )

    @commands.command()
    @checks.is_dm()
    async def removealias(self, ctx: Context, alias: str):
        """Create a personal alias for a command.

        alias: The alias to be created.
        command: The command to create the alias for.
        """
        preferences = load_preferences(ctx.message.author)
        try:
            del preferences.aliases[alias]
            preferences.save_preferences()
            await safe_send(ctx, f"Successfully deleted your alias {alias}.")
        except KeyError:
            raise commands.BadArgument(f"You do not have an alias {alias}.")

    @commands.command()
    @checks.is_dm()
    async def setnick(self, ctx: Context, *, nick: str):
        """Set your nickname for bot messages.

        nick: The name you want to use.

        This input is case-sensitive.
        """
        preferences = load_preferences(ctx.message.author)
        preferences.nick = nick
        preferences.save_preferences()
        await safe_send(ctx, f"Successfully set your nickname to {nick}.")

    @commands.command()
    @checks.is_dm()
    async def setpronouns(
        self,
        ctx: Context,
        subjective: str,
        objective: str,
        adjective: str,
        posessive: str,
        reflexive: str,
        plural: str = "no",
    ):
        """Set your pronouns for bot messages.

        subjective: The subjective pronoun, for instance 'they' or 'she'.
        objective: The objective pronoun, for instance 'them' or 'her'.
        adjective: The posessive adjective, for instance 'their' or 'her'.
        posessive: The posessive pronoun, for instance 'theirs' or 'hers'.
        reflexive: The reflexive pronoun, for instance 'themselves' or 'herself'.
        plural: Whether the bot should use plural grammar with your pronouns.
            For instance, 'they are about to die' or 'she is about to die'.

        You can also fill in the blank:
            [subjective] is/are the Imp.
            The Imp is [objective].  # TODO: this is apparently bad grammar
            It is [adjective] character.
            The character is [posessive].
            [subjective] made the Minion a Demon by targeting [reflexive].

        For example:
            They are the Imp.
            The Imp is them.
            It is their character.
            The character is theirs.
            They made the Minion a Demon by targetting themselves.

        These inputs are case-insensitive.

        If you use this to mock trans people, I will blacklist you from using the bot. <3
        """
        plural_actual = to_bool(plural, "argument")

        preferences = load_preferences(ctx.message.author)
        preferences.pronouns = (
            subjective,
            objective,
            adjective,
            posessive,
            reflexive,
            plural_actual,
        )
        preferences.save_preferences()
        await safe_send(
            ctx,
            (
                "Successfully set your pronouns! "
                "You are valid and thank you for trusting me with them!\n"
                "Here's a quick example so you can make sure you got the grammar right:"
                "\n{subjective} {verb} the Imp."
                "\nThe Imp is {objective}."
                "\nIt is {adjective} character."
                "\nThe character is {posessive}."
                "\n{subjective} made the Minion a Demon by targeting {reflexive}."
            ).format(
                reflexive=reflexive,
                subjective=subjective.capitalize(),
                verb=["is", "are"][plural_actual],
                objective=objective,
                adjective=adjective,
                posessive=posessive,
            ),
        )

    @commands.command(hidden=True)
    @checks.is_dm()
    async def emergencyvote(
        self, ctx: Context, vote: str, time: int, specific: str = "yes",
    ):
        """Change your emergency vote.

        vote: The vote you want to set, yes or no.
        time: The time in minutes for the vote to trigger.
        specific: Whether this emergency is bot-specific, yes or no. Defaults to yes.
        """
        vote_actual = to_bool(vote, "vote")
        specific_actual = to_bool(specific, "argument")
        preferences = load_preferences(ctx.message.author)
        if specific_actual:
            preferences.specific_emergencys[ctx.bot.user.id] = (vote_actual, time)
            preferences.save_preferences()
            await safe_send(
                ctx,
                (
                    "Successfully set a emergency vote of {vote} "
                    "in {time} minutes for {botName}."
                ).format(
                    vote=("no", "yes")[vote_actual],
                    time=str(time),
                    botName=ctx.bot.server.get_member(ctx.bot.user.id).display_name,
                ),
            )
        else:
            preferences.emergency_vote = (vote_actual, time)
            preferences.save_preferences()
            await safe_send(
                ctx,
                (
                    "Successfully set a generic emergency vote of "
                    "{vote} in {time} minutes."
                ).format(vote=("no", "yes")[vote_actual], time=str(time)),
            )

    @commands.command(hidden=True)
    @checks.is_dm()
    async def removeemergencyvote(self, ctx: Context, specific: str = "yes"):
        """Remove your emergency vote.

        specific: Whether to remove the bot-specific emergency vote or the generic one.
        """
        specific_actual = to_bool(specific, "argument")
        preferences = load_preferences(ctx.message.author)
        if specific_actual:
            try:
                del preferences.specific_emergencys[ctx.bot.user.id]
                preferences.save_preferences()
                await safe_send(
                    ctx,
                    (
                        "Successfully removed your bot-specific emergency vote. "
                        "Please note any generic emergency vote will now apply."
                    ),
                )
            except KeyError:
                await safe_send(
                    ctx,
                    "You do not have a specific emergency vote with {botName}.".format(
                        botName=ctx.bot.server.get_member(ctx.bot.user.id).display_name
                    ),
                )
        else:
            if preferences.emergency_vote[1] is not None:
                preferences.emergency_vote = (0, None)
                preferences.save_preferences()
                await safe_send(
                    ctx,
                    (
                        "Successfully removed your generic emergency vote. "
                        "Please note any bot-specific emergency votes will still apply."
                    ),
                )
            else:
                await safe_send(ctx, "You do not have a generic emergency vote.")


def setup(bot: BOTCBot):
    """Set the cog up."""
    bot.add_cog(PreferenceManagement(bot))
