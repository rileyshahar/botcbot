"""Runs the bot.

Call this with an argument (which can include spaces) representing the bot's folder.
"""

from configparser import ConfigParser
from sys import exit as sysexit, argv

from lib.bot import BOTCBot
from lib.typings.context import Context

bot_name = " ".join(argv[1:])

config = ConfigParser()
config.read("config.ini")

# Define the bot
try:
    bot = BOTCBot(
        bot_name,
        int(config[bot_name]["server"]),
        int(config[bot_name]["channel"]),
        int(config[bot_name]["storytellerid"]),
        int(config[bot_name]["playerid"]),
        int(config[bot_name]["inactiveid"]),
        int(config[bot_name]["playtestid"]),
        int(config[bot_name]["observerid"]),
        config=config[bot_name],
        command_prefix=tuple([x for x in config[bot_name]["prefixes"]]),
        description=(
            "An unofficial Discord bot for helping run games of Blood on the "
            "Clocktower. \nThis bot is in beta and is not associated with BOTC or "
            "TPI. Please be forgiving of bugs.\n\nI'm Riley - message me "
            "(nihilistkitten#6937) with questions, feedback, bug reports, or just "
            "to talk!\n\nFor new players: the Gameplay and Preferences categories "
            "are most relevant to you."
        ),
        case_insensitive=True,
        owner_id=149969652141785088,
    )
except KeyError as e:
    if str(e) == f"'{bot_name}'":
        print(f'Bot "{bot_name}" not found.')
        print("Shutting down.")
        sysexit()
    else:
        print(f'Key {str(e)} not defined in config.ini for "{bot_name}".')
        print("Shutting down.")
        sysexit()


# Backup wrapper
# noinspection PyUnboundLocalVariable
# if we get here, bot is guaranteed to be defined
@bot.after_invoke
async def command_cleanup(ctx: Context):
    """Run after every command.

    Backs up the bot and updates the status.
    """
    if ctx.bot.game:
        await ctx.bot.game.reseat(ctx, ctx.bot.game.seating_order)
    ctx.bot.backup()
    await ctx.bot.update_status()


# Load extensions
bot.load_extension("lib.cogs.events")
bot.load_extension("lib.cogs.debug")
bot.load_extension("lib.cogs.storytelling")
bot.load_extension("lib.cogs.playing")
bot.load_extension("lib.cogs.script_management")
bot.load_extension("lib.cogs.preference_management")
bot.load_extension("lib.cogs.effect_management")

# Run the bot
if __name__ == "__main__":
    bot.run(config[bot_name]["TOKEN"])
