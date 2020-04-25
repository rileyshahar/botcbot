"""Sets up a new bot."""

from configparser import ConfigParser
from os import mkdir


def while_not_int(text: str) -> str:
    while True:
        out = input(f"What is the {text} ID?\n")
        try:
            int(out)
            break
        except ValueError:
            print(f"The {text} ID must be an integer.")
    return out


if __name__ == "__main__":
    config = ConfigParser()
    config.read("config.ini")

    while True:
        bot_name = input("What is the bot's name?\n")
        if bot_name not in config:
            break
        print(f"A bot named {bot_name} already exists.")

    config[bot_name] = {}

    config[bot_name]["Server"] = while_not_int("server")
    config[bot_name]["Channel"] = while_not_int("gameplay")
    config[bot_name]["StorytellerID"] = while_not_int("Storyteller role")
    config[bot_name]["PlayerID"] = while_not_int("Player role")
    config[bot_name]["InactiveID"] = while_not_int("Inactive role")
    config[bot_name]["ObserverID"] = while_not_int("Observer role")

    while True:
        try:
            config[bot_name]["Playtest"] = input("Is this a playtest bot?\n")
            config[bot_name].getboolean("Playtest")
            break
        except ValueError:
            print('You must answer with a valid boolean; try "yes" or "no".')

    if config[bot_name].getboolean("Playtest"):
        config[bot_name]["PlaytestID"] = while_not_int("Playtest role")
    else:
        config[bot_name]["PlaytestID"] = "None"

    config[bot_name]["TOKEN"] = input("What is the bot's token?\n")
    with open("config.ini", "w") as configfile:
        config.write(configfile)

    mkdir("resources/backup/" + bot_name)
    mkdir("resources/backup/" + bot_name + "/old")

    # TODO: tmux stuff maybe

    print(f"Successfully created {bot_name}.")
