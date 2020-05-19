"""Contains the Script class and script_list generator."""

from os import listdir
from typing import List, Generator, Type, Tuple

from dill import dump, load

from resources.basegame import characters

try:
    # noinspection PyUnresolvedReferences
    from resources.playtest import playtestcharacters
except ImportError:
    pass

from lib.logic.Character import Character, Townsfolk, Outsider, Minion, Demon
from lib.typings.context import Context
from lib.utils import list_to_plural_string


class Script:
    """Stores information about a specific script.

    Parameters
    ----------
    name : str
        The scripts's name.
    character_input : List[Type[Character]]
        The characters on the script.
    aliases : List[str]
        The script's aliases.
    first_night : List[Type[Character]]
        The first night _order.
    other_nights : List[Type[Character]]
        The _order for other nights.
    editors : List[int]
        IDs of users authorized to edit the script.
    playtest : bool
        Whether the script is playtest-only.

    Attributes
    ----------
    name
    character_input
    aliases
    editors
    playtest
    first_night
    other_nights
    """

    aliases: List[str]
    editors: List[int]
    first_night: List[Type[Character]]
    other_nights: List[Type[Character]]

    def __init__(
        self,
        name: str,
        character_input: List[Type[Character]],
        aliases: List[str] = None,
        first_night: List[Type[Character]] = None,
        other_nights: List[Type[Character]] = None,
        editors: List[int] = None,
        playtest: bool = False,
    ):
        self.name = name
        self.character_list = character_input
        self.aliases = aliases or []
        self.editors = editors or []
        self.playtest = playtest
        self.first_night = first_night or []
        self.other_nights = other_nights or []

    def has_character(self, character: Character) -> bool:
        """Whether character is on the script."""
        return character in self.character_list

    @property
    def has_atheist(self) -> bool:
        """Whether the atheist is on the script."""
        try:
            return self.has_character(playtestcharacters.Atheist.Atheist)
        except NameError:
            return False

    def save(self):
        """Save the script."""
        if self.playtest:
            with open(
                "resources/playtest/scripts/" + self.name + ".pckl", "wb"
            ) as file:
                dump(self, file)
        else:
            with open(
                "resources/basegame/scripts/" + self.name + ".pckl", "wb"
            ) as file:
                dump(self, file)

    def info(self, ctx: Context) -> Generator[str, None, None]:
        """Return a generator with information about the script."""
        # maybe we should do more specific message length handling here than in safe_send

        with ctx.typing():
            message_text = f"**__{self.name}:__**"
            message_text += self._character_type_info(Townsfolk)
            yield message_text  # we want to separate townsfolk from other characters

            message_text = ""
            for cls in (Outsider, Minion, Demon):
                message_text += self._character_type_info(cls)
            yield message_text

            message_text = "__First Night:__\nDusk\nMinion Info\nDemon Info"
            for character in self.first_night:
                message_text += "\n" + character.name
            message_text += "\nDawn"

            message_text += "\n\n__Other Nights:__\nDusk"
            for character in self.other_nights:
                message_text += "\n" + character.name
            message_text += "\nDawn"

            yield message_text

    def editor_names(self, ctx: Context) -> Tuple[str, bool]:
        """Determine the names of the bot's editors."""
        names = []
        for idn in self.editors:
            user = ctx.bot.get_user(idn)
            names.append(f"{user.name}#{user.discriminator}")

        return list_to_plural_string(names, "no one")

    def short_info(self, ctx: Context) -> str:
        """Format a short-form summary of script info."""
        aliases = list_to_plural_string(self.aliases, "none")[0]
        editors = (self.editor_names(ctx))[0]
        return f"**{self.name}:**\n> Aliases: {aliases}\n> Editors: {editors}"

    def _character_type_info(self, cls: Type["Character"]) -> str:
        """Generate a list of characters of cls type."""
        s = "" if cls == Townsfolk else "s"
        out = f"\n\n__{cls.__name__}{s}:__"
        for character in self.character_list:
            if issubclass(character, cls):
                out += "\n> **{char_name}** - {char_rules}".format(
                    char_name=character.name, char_rules=character.rules_text(),
                )
        return out


def script_list(ctx: Context, playtest: bool = False) -> Generator[Script, None, None]:
    """Find all scripts.

    Parameters
    ----------
    ctx : Context
        The invocation context.
    playtest : bool
        Whether to find playtest scripts.

    Yields
    ------
    Script
        Default scripts, or scripts stored in resources.
    """
    # Add the three default scripts
    # not sure this will work so it needs testing
    yield Script(
        "Trouble Brewing",
        [
            characters.Investigator,
            characters.Chef,
            characters.Washerwoman,
            characters.Librarian,
            characters.Empath,
            characters.FortuneTeller,
            characters.Undertaker,
            characters.Monk,
            characters.Slayer,
            characters.Soldier,
            characters.Ravenkeeper,
            characters.Virgin,
            characters.Mayor,
            characters.Butler,
            characters.Saint,
            characters.Recluse,
            characters.Drunk,
            characters.Poisoner,
            characters.Spy,
            characters.Baron,
            characters.ScarletWoman,
            characters.Imp,
        ],
        first_night=[
            characters.Poisoner,
            characters.Washerwoman,
            characters.Librarian,
            characters.Chef,
            characters.Investigator,
            characters.Empath,
            characters.FortuneTeller,
            characters.Butler,
            characters.Spy,
        ],
        other_nights=[
            characters.Poisoner,
            characters.Monk,
            characters.ScarletWoman,
            characters.Imp,
            characters.Ravenkeeper,
            characters.Empath,
            characters.FortuneTeller,
            characters.Butler,
            characters.Undertaker,
            characters.Spy,
        ],
        aliases=["TB"],
        editors=[],
    )
    # noinspection DuplicatedCode
    yield Script(
        "Bad Moon Rising",
        [
            characters.Grandmother,
            characters.Sailor,
            characters.Chambermaid,
            characters.Innkeeper,
            characters.Gambler,
            characters.Exorcist,
            characters.Gossip,
            characters.Courtier,
            characters.Professor,
            characters.Fool,
            characters.Pacifist,
            characters.TeaLady,
            characters.Minstrel,
            characters.Tinker,
            characters.Moonchild,
            characters.Goon,
            characters.Lunatic,
            characters.Godfather,
            characters.DevilSAdvocate,
            characters.Assassin,
            characters.Mastermind,
            characters.Pukka,
            characters.Shabaloth,
            characters.Po,
            characters.Zombuul,
        ],
        first_night=[
            characters.Lunatic,
            characters.Sailor,
            characters.Courtier,
            characters.Godfather,
            characters.DevilSAdvocate,
            characters.Pukka,
            characters.Grandmother,
            characters.Chambermaid,
            characters.Goon,
        ],
        other_nights=[
            characters.Sailor,
            characters.Innkeeper,
            characters.Courtier,
            characters.DevilSAdvocate,
            characters.Gambler,
            characters.Exorcist,
            characters.Lunatic,
            characters.Zombuul,
            characters.Pukka,
            characters.Shabaloth,
            characters.Po,
            characters.Assassin,
            characters.Gossip,
            characters.Tinker,
            characters.Moonchild,
            characters.Godfather,
            characters.Professor,
            characters.Chambermaid,
            characters.Goon,
        ],
        aliases=["BMR"],
        editors=[],
    )
    # noinspection DuplicatedCode
    yield Script(
        "Sects & Violets",
        [
            characters.Clockmaker,
            characters.Dreamer,
            characters.SnakeCharmer,
            characters.Mathematician,
            characters.Flowergirl,
            characters.TownCrier,
            characters.Oracle,
            characters.Savant,
            characters.Artist,
            characters.Seamstress,
            characters.Philosopher,
            characters.Juggler,
            characters.Sage,
            characters.Sweetheart,
            characters.Mutant,
            characters.Barber,
            characters.Klutz,
            characters.EvilTwin,
            characters.Witch,
            characters.Cerenovus,
            characters.PitHag,
            characters.NoDashii,
            characters.Vigormortis,
            characters.FangGu,
            characters.Vortox,
        ],
        first_night=[
            characters.Philosopher,
            characters.SnakeCharmer,
            characters.EvilTwin,
            characters.Witch,
            characters.Cerenovus,
            characters.Clockmaker,
            characters.Dreamer,
            characters.Seamstress,
            characters.Mathematician,
        ],
        other_nights=[
            characters.Philosopher,
            characters.SnakeCharmer,
            characters.Witch,
            characters.Cerenovus,
            characters.PitHag,
            characters.FangGu,
            characters.NoDashii,
            characters.Vortox,
            characters.Vigormortis,
            characters.Barber,
            characters.Sage,
            characters.Dreamer,
            characters.Seamstress,
            characters.Flowergirl,
            characters.TownCrier,
            characters.Oracle,
            characters.Juggler,
            characters.Mathematician,
        ],
        aliases=["Sects and Violets", "SV", "S&V", "SnV"],
        editors=[],
    )

    # get custom scripts from resources
    for filename in listdir("resources/basegame/scripts/"):
        if filename.endswith(".pckl"):
            with open("resources/basegame/scripts/" + filename, "rb") as file:
                script: Script = load(file)
                yield script

    if playtest:
        for filename in listdir("resources/playtest/scripts/"):
            if filename.endswith(".pckl"):
                with open("resources/playtest/scripts/" + filename, "rb") as file:
                    script: Script = load(file)
                    yield script
