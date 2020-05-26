"""Runs the bot.

Call this with an argument (which can include spaces) representing the bot's name.
"""

from configparser import ConfigParser
from os import listdir
from sys import argv
from sys import exit as sysexit

from lib.bot import BOTCBot
from lib.typings.context import Context

BOT_NAME = " ".join(argv[1:])

config = ConfigParser()
config.read("config.ini")

# Define the bot
try:
    bot = BOTCBot(
        BOT_NAME,
        int(config[BOT_NAME]["server"]),
        int(config[BOT_NAME]["channel"]),
        int(config[BOT_NAME]["storytellerid"]),
        int(config[BOT_NAME]["playerid"]),
        int(config[BOT_NAME]["inactiveid"]),
        int(config[BOT_NAME]["playtestid"]),
        int(config[BOT_NAME]["observerid"]),
        config=config[BOT_NAME],
        command_prefix=tuple(config[BOT_NAME]["prefixes"]),
        description=(
            "An unofficial Discord bot for helping run games of Blood on the "
            "Clocktower. \nThis bot is in beta and is not associated with BOTC or "
            "TPI. Please be forgiving of bugs.\n\nI'm Riley - message me "
            "(nihilistkitten#6937) with questions, feedback, bug reports, or just "
            "to talk!"
        ),
        case_insensitive=True,
        owner_id=149969652141785088,
    )
except KeyError as error:
    if str(error) == f"'{BOT_NAME}'":
        print(f'Bot "{BOT_NAME}" not found.')
        print("Shutting down.")
        sysexit()
    else:
        print(f'Key {str(error)} not defined in config.ini for "{BOT_NAME}".')
        print("Shutting down.")
        sysexit()


# Backup wrapper
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
for file in listdir("lib/cogs"):
    if file.endswith(".py") and not file.startswith("_"):
        bot.load_extension("lib.cogs." + file[:-3])

# Run the bot
if __name__ == "__main__":
    bot.run(config[BOT_NAME]["TOKEN"])
