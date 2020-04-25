"""Contains the preferences class and load_preferences funciton."""

from typing import Dict, Tuple, Optional, Union, TYPE_CHECKING

from dill import load, dump
from discord import Member

if TYPE_CHECKING:
    from lib.logic.Player import Player


class Preferences:
    """Stores a member's global preferences.

    Parameters
    ----------
    member : Union[Player, Member]
        The person whose preferences are being stored.

    Attributes
    ----------
    aliases : Dict[str, str]
        Command aliases: [alias, command].
    nick : str
        The bot nickname.
    pronouns : Tuple[str, str, str, str, str, bool]
        A list of pronouns.
    emergency_vote : Tuple[int, Optional[int]]
        A global emergency vote.
    specific_emergencys : Dict[int, Tuple[bool, int]]
        A list of bot-specific emergency votes.
    id : int
        The member's discord id.
    """

    aliases: Dict[str, str]
    emergency_vote: Tuple[int, Optional[int]]
    specific_emergencys: Dict[int, Tuple[bool, int]]
    nick: str

    def __init__(self, member: Union["Player", Member]):
        self.aliases = {}
        self.nick = member.display_name
        self.pronouns = (
            "they",
            "them",
            "their",
            "theirs",
            "themselves",
            True,
        )
        self.emergency_vote = (0, None)
        self.specific_emergencys = {}
        self.id = member.id

    def save_preferences(self):
        """Save preferences."""
        with open("resources/preferences/" + str(self.id) + ".pckl", "wb") as file:
            dump(self, file)

    def get_emergency_vote(self, bot_id: int) -> Tuple[int, Optional[int]]:
        """Generate the (potentially bot-specific) emergency vote.

        Parameters
        ----------
        bot_id : int
            The bot's ID number.

        Returns
        -------
        Tuple[int, Optional[int]]
            The default vote.
        """
        try:
            return self.specific_emergencys[bot_id]
        except KeyError:
            return self.emergency_vote


def load_preferences(member: Union["Player", Member]) -> Preferences:
    """Load a member's preferences.

    Parameters
    ----------
    member : Union[Player, Member]
        The preferences to load.

    Returns
    -------
    Preferences
        The member's preferences.
    """
    try:
        with open("resources/preferences/" + str(member.id) + ".pckl", "rb") as file:
            return load(file)
    except FileNotFoundError:
        return Preferences(member)
