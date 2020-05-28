"""Contains tools for managing game logic."""
import itertools
from typing import TYPE_CHECKING, Callable, Dict, List

import numpy as np

from lib.utils import list_to_plural_string

if TYPE_CHECKING:
    from lib.logic.Player import Player
    from lib.logic.Game import Game
    from lib.typings.context import Context


def generate_game_info_message(order, game: "Game") -> str:
    """Generate a game _order message.

    Parameters
    ----------
    order : List[Player]
        The _order of players.
    game : Game
        The invocation context.

    Returns
    -------
    str
        A message representing the seating order and other info about the game.

    Notes
    -----
    # TODO: there may be deep underlying issues here with Game being None
    # that will require this function to be separated into two cases, for a new game
    # and for change during the game
    """
    message_text = ""
    for text in (
        _generate_seating_order_message(game, order),
        _generate_distribution_message(game, order),
        _generate_day_info_message(game, order),
    ):
        message_text += "\n\n" + text
    return message_text


def _generate_seating_order_message(game: "Game", order: List["Player"]) -> str:
    """Generate the seating order part of the game info message."""
    message_text = "**Seating Order:**"
    for player in order:
        message_text += _generate_player_line(game, player)
    return message_text


def _generate_player_line(game: "Game", player: "Player") -> str:
    """Generate an individual's player line in the seating order message."""
    message_text = "\n"

    if player.ghost(game, registers=True):
        message_text += f"~~{player.nick}~~ "

        dead_votes = "O" * player.dead_votes
        if dead_votes == "":
            dead_votes = "X"
        message_text += dead_votes

    else:
        message_text += player.nick
    message_text += player.character.seating_order_addendum
    return message_text


def _generate_distribution_message(game: "Game", order: List["Player"]):
    """Generate the distribution part of the game info message."""
    n = len([x for x in order if not x.is_status(game, "traveler")])
    if n == 5:
        distribution = ("3", "0", "1")
    elif n == 6:
        distribution = ("3", "1", "1")
    elif 7 <= n <= 15:
        o = int((n - 1) % 3)
        m = int(np.floor((n - 1) / 3) - 1)
        distribution = (str(n - (o + m + 1)), str(o), str(m))
    else:
        distribution = ("Unknown", "Unknown", "Unknown")
    outsider_plural = "s" if distribution[1] != 1 else ""
    minion_plural = "s" if distribution[2] != 1 else ""
    message_text = (
        f"There are {str(n)} non-Traveler players. The default distribution is "
        f"{distribution[0]} Townsfolk, {distribution[1]} Outsider{outsider_plural}, "
        f"{distribution[2]} Minion{minion_plural}, and 1 Demon."
    )
    return message_text


def _generate_day_info_message(game: "Game", order: List["Player"]) -> str:
    """Generate info about the current day or night."""
    if not game or not game.current_day:
        message_text = "It is Night "
        try:
            message_text += str(game.day_number + 1) + "."
        except AttributeError:
            message_text += "1."

    else:
        message_text = f"It is Day {game.day_number}.\n"
        skip_list = [player.nick for player in order if player.has_skipped]
        if not skip_list:
            message_text += "No players have skipped."
        else:
            skip_str = list_to_plural_string(skip_list, "none")
            verb = ("has", "have")[skip_str[1]]
            message_text += f"{skip_str[0]} {verb} skipped."

    return message_text


def generate_message_tally(ctx: "Context", condition: Callable[[Dict], bool]):
    """Generate a tally of messages."""
    # TODO: clean this up lol
    message_tally = {
        X: 0 for X in itertools.combinations(ctx.bot.game.seating_order, 2)
    }
    for person in ctx.bot.game.seating_order:
        for msg in person.message_history:
            if msg["from"] == person:
                if condition(msg):
                    if (person, msg["to"]) in message_tally:
                        message_tally[(person, msg["to"])] += 1
                    elif (msg["to"], person) in message_tally:
                        message_tally[(msg["to"], person)] += 1
                    else:
                        message_tally[(person, msg["to"])] = 1
    sorted_tally = sorted(message_tally.items(), key=lambda x: -x[1])
    message_text = "**Message Tally**:"
    for pair in sorted_tally:
        if pair[1] > 0:
            message_text += "\n> {person1} - {person2}: {n}".format(
                person1=pair[0][0].nick, person2=pair[0][1].nick, n=pair[1]
            )
        else:
            message_text += "\n> All other pairs: 0"
            break
    return message_text
