"""Contains the Effect class and several Effect subclass ABCs."""

from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from lib.logic.Player import Player
    from lib.logic.Game import Game

# TODO: add user-facing names for statuses

status_list = [
    "poisoned",  # The player is poisoned.
    "drunk",  # The player is drunk.
    "dead",  # The player is dead.
    "not_functioning",  # The player's ability is not functioning.
    "safe",  # The player is generally protected.
    "safe_from_demon",  # The player is protected from the demon.
    "thiefed",  # Vote counts negative (caused by thief).
    "bureaucrated",  # Vote counts thrice (caused by bureaucrat).
    "used_ability",  # A one-time-use character has used their ability.
    "can_dead_vote_without_token",  # Voting while dead won't use or require a dead vote.
    "can_nominate_while_dead",  # The player can nominate while dead.
    "can_nominate_twice",  # The player can nominate twice.
    "can_vote_twice",  # The player can vote twice.
    "good",  # The player is good.
    "evil",  # The player is evil.
    "townsfolk",  # The player is a Townsfolk.
    "outsider",  # The player is an Outsider.
    "minion",  # The player is a Minon.
    "demon",  # The player is a Demon.
    "traveler",  # The player is a Traveler.
    "storyteller",  # The player is a Storyteller.
]


class Effect:
    """Stores information about a game effect.

    Parameters
    ----------
    affected_player : Player
        The player affected by the effect.
    source_player : Player
        The player who is causing the effect, or None if a storyteller.

    Attributes
    ----------
    appears : bool
        Whether the effect appears in the grimoire by default.
    disabled: bool
        Whether the effect is currently disabled.
    affected_player
    source_player
    """

    def __init__(
        self, affected_player: "Player", source_player: "Player",
    ):
        self.affected_player = affected_player
        self.source_player = source_player
        self._name = "Effect"
        self.appears = True
        self.disabled = False

    @property
    def name(self):
        """Determine the effect's name."""
        return self._name

    def status(self, game: "Game", status_name: str) -> bool:
        """Determine whether the effect causes a status.

        Parameters
        ----------
        game : Game
            The current game.
        status_name : str
            The status to be checked.

        Returns
        -------
        bool
            Whether the effect causes the status.
        """
        if self.disabled:
            return False

        assert status_name in status_list

        try:
            return getattr(self, status_name)(game)

        except AttributeError:
            if status_name == "not_functioning":
                return (
                    self.status(game, "poisoned")
                    or self.status(game, "drunk")
                    or self.status(game, "dead")
                )

            if status_name == "safe_from_demon":
                return self.status(game, "safe")

            return False

    def registers_status(self, game: "Game", status_name: str) -> bool:
        """Determine whether the effect causes registering as a status.

        Parameters
        ----------
        game : Game
            The current game.
        status_name : str
            The status to be checked.

        Returns
        -------
        bool
            Whether the effect causes registering as the status.
        """
        if self.disabled:
            return False

        assert status_name in status_list
        return getattr(self, "registers_" + status_name, lambda x: False)(game)

    def morning_cleanup(self, game: "Game"):
        """Call at the start of each day.

        Primarily used to delete effects, when appropriate.
        """
        pass

    # noinspection PyUnusedLocal
    @staticmethod
    async def nomination(game: "Game", nominee: "Player", nominator: "Player") -> bool:
        """Call at the start of each nomination.

        Parameters
        ----------
        game : Game
            The current game.
        nominee : Player
            The nominee.
        nominator : Player
            The nominator.

        Returns
        -------
        bool
            Whether to go through with the nomination.
        """
        return True

    def evening_cleanup(self, game: "Game"):
        """Call at the end of each day.

        Primarily used to delete effects, when appropriate.
        """
        pass

    def source_drunkpoisoned_cleanup(self, game: "Game"):
        """Call when source_player stops functioning.

        Primarily used to disable effects, when appropriate.
        """
        pass

    def source_death_cleanup(self, game: "Game"):
        """Call when source_player dies.

        Primarily used to delete effects, when appropriate.
        """
        pass

    def turn_on(self, game: "Game", enabler_func: Callable[[], None]) -> "Effect":
        """Turn on the effect.

        Parameters
        ----------
        game : Game
            The current game.
        enabler_func : Callable [[], None]
            A function which enables the effect in some way.

        Notes
        -----
        The effect should be disabled in some way (either by not being a in
        affected_player.effects, or because self.disabled = True) before this method id
        called. This checks if the effect being enabled causes the player to die or stop
        functioning via checking the player's state before enabler_func is called and
        then comparing it to the state after. If it causes death or drunkpoisoning, the
        appropriate modifiers are also called.
        """
        originally_functioning = self.affected_player.functioning(game)
        originally_dead = self.affected_player.ghost(game)

        enabler_func()

        if originally_functioning and not self.affected_player.functioning(game):

            if not originally_dead and self.affected_player.ghost(game):
                for effect in self.affected_player.source_effects(game):
                    # can't call it on self because of recursion errors
                    if not self == effect:
                        effect.source_death_cleanup(game)

            else:
                for effect in self.affected_player.source_effects(game):
                    if not self == effect:
                        effect.source_drunkpoisoned_cleanup(game)

        return self

    def disable(self, game: "Game"):
        """Handle disabling of the effect."""

        def disabler_func():
            """Disable the effect."""
            self.disabled = True

        self.turn_off(game, disabler_func)

    def delete(self, game: "Game"):
        """Handle deletion of the effect."""

        def disabler_func():
            """Delete the effect."""
            self.affected_player.effects.remove(self)

        self.turn_off(game, disabler_func)

    def turn_off(self, game: "Game", disabler_func: Callable[[], None]):
        """Turn off the effect.

        For more details, see the turn_on documentation."""
        originally_functioning = self.affected_player.functioning(game)

        disabler_func()

        if not originally_functioning and self.affected_player.functioning(game):
            for effect in self.affected_player.source_effects(game):
                effect.source_starts_functioning(game)

    def source_starts_functioning(self, game: "Game"):
        """Call when source_player restarts functioning.

        Modified by decorators (defined in logic.tools) to call self.turn_on."""
        pass


# Some generic single-status effects that can be caused by storytellers
class Drunk(Effect):
    """Makes the player drunk."""

    def __init__(
        self, affected_player: "Player", source_player: "Player",
    ):
        super().__init__(affected_player, source_player)
        self._name = "Drunk"

    # noinspection PyUnusedLocal
    @staticmethod
    def drunk(game: "Game") -> bool:
        """Determine whether the effect causes drunkenness."""
        return True


class Poisoned(Effect):
    """Makes the player poisoned."""

    def __init__(
        self, affected_player: "Player", source_player: "Player",
    ):
        super().__init__(affected_player, source_player)
        self._name = "Poisoned"

    # noinspection PyUnusedLocal
    @staticmethod
    def poisoned(game: "Game") -> bool:
        """Determine whether the effect causes poisoning."""
        return True


class Dead(Effect):
    """Makes the player dead."""

    def __init__(
        self, affected_player: "Player", source_player: "Player",
    ):
        super().__init__(affected_player, source_player)
        self._name = "Dead"

    # noinspection PyUnusedLocal
    @staticmethod
    def dead(game: "Game") -> bool:
        """Determine whether the effect causes death."""
        return True


class Safe(Effect):
    """Makes the player safe."""

    def __init__(
        self, affected_player: "Player", source_player: "Player",
    ):
        super().__init__(affected_player, source_player)
        self._name = "Safe"

    # noinspection PyUnusedLocal
    @staticmethod
    def safe(game: "Game") -> bool:
        """Determine whether the effect causes safety."""
        return True


class SafeFromDemon(Effect):
    """Makes the player safe from the demon."""

    def __init__(
        self, affected_player: "Player", source_player: "Player",
    ):
        super().__init__(affected_player, source_player)
        self._name = "Safe From Demon"

    # noinspection PyUnusedLocal
    @staticmethod
    def safe_from_demon(game: "Game") -> bool:
        """Determine whether the effect causes safety from the Demon."""
        return True


class UsedAbility(Effect):
    """For one-time-use characters who have used their ability."""

    def __init__(
        self, affected_player: "Player", source_player: "Player",
    ):
        super().__init__(affected_player, source_player)
        self._name = "Used Ability"

    # noinspection PyUnusedLocal
    @staticmethod
    def used_ability(game: "Game") -> bool:
        """Determine whether the effect causes the ability to be used."""
        return True


class NoDeadVoteNeeded(Effect):
    """For effects which allow voting without a dead vote."""

    def __init__(
        self, affected_player: "Player", source_player: "Player",
    ):
        super().__init__(affected_player, source_player)
        self._name = "Infinite Dead Votes"

    # noinspection PyUnusedLocal
    @staticmethod
    def can_dead_vote_without_token(game: "Game") -> bool:
        """Determine whether the effect allows dead voting without a token."""
        return True


# Alignment and character type classes for lib.logic.Character
class Good(Effect):
    """Makes the player good."""

    def __init__(
        self, affected_player: "Player", source_player: "Player",
    ):
        super().__init__(affected_player, source_player)
        self._name = "Good"
        self.appears = False

    # noinspection PyUnusedLocal
    @staticmethod
    def good(game: "Game") -> bool:
        """Determine whether the effect makes the player good."""
        return True


class Evil(Effect):
    """Makes the player evil."""

    def __init__(
        self, affected_player: "Player", source_player: "Player",
    ):
        super().__init__(affected_player, source_player)
        self._name = "Evil"
        self.appears = False

    # noinspection PyUnusedLocal
    @staticmethod
    def evil(game: "Game") -> bool:
        """Determine whether the effect makes the player evil."""
        return True


class TownsfolkEffect(Effect):
    """Makes the player a Townsfolk."""

    def __init__(
        self, affected_player: "Player", source_player: "Player",
    ):
        super().__init__(affected_player, source_player)
        self._name = "Townsfolk"
        self.appears = False

    # noinspection PyUnusedLocal
    @staticmethod
    def townsfolk(game: "Game") -> bool:
        """Determine whether the effect makes the player a townsfolk."""
        return True


class OutsiderEffect(Effect):
    """Makes the player an Outsider."""

    def __init__(
        self, affected_player: "Player", source_player: "Player",
    ):
        super().__init__(affected_player, source_player)
        self._name = "Outsider"
        self.appears = False

    # noinspection PyUnusedLocal
    @staticmethod
    def outsider(game: "Game") -> bool:
        """Determine whether the effect makes the player an outsider."""
        return True


class MinionEffect(Effect):
    """Makes the player a Minion."""

    def __init__(
        self, affected_player: "Player", source_player: "Player",
    ):
        super().__init__(affected_player, source_player)
        self._name = "Minion"
        self.appears = False

    # noinspection PyUnusedLocal
    @staticmethod
    def minion(game: "Game") -> bool:
        """Determine whether the effect makes the player a minion."""
        return True


class DemonEffect(Effect):
    """Makes the player a Demon."""

    def __init__(
        self, affected_player: "Player", source_player: "Player",
    ):
        super().__init__(affected_player, source_player)
        self._name = "Demon"
        self.appears = False

    # noinspection PyUnusedLocal
    @staticmethod
    def demon(game: "Game") -> bool:
        """Determine whether the effect makes the player a demon."""
        return True


class TravelerEffect(Effect):
    """Makes the player a Traveler."""

    def __init__(
        self, affected_player: "Player", source_player: "Player",
    ):
        super().__init__(affected_player, source_player)
        self._name = "Traveler"
        self.appears = False

    # noinspection PyUnusedLocal
    @staticmethod
    def traveler(game: "Game") -> bool:
        """Determine whether the effect makes the player a traveler."""
        return True


class StorytellerEffect(Effect):
    """Makes the player a Storyteller."""

    def __init__(
        self, affected_player: "Player", source_player: "Player",
    ):
        super().__init__(affected_player, source_player)
        self._name = "Storyteller"
        self.appears = False

    # noinspection PyUnusedLocal
    @staticmethod
    def storyteller(game: "Game") -> bool:
        """Determine whether the effect makes the player a storyteller."""
        return True


class RegistersGood(Effect):
    """Makes a character register as Good."""

    def __init__(self, affected_player, source_player):
        super().__init__(affected_player, source_player)
        self._name = "Registers as Good"

    # noinspection PyUnusedLocal
    @staticmethod
    def registers_good(game: "Game"):
        """Determine whether the effect makes the player register as good."""
        return True


class RegistersEvil(Effect):
    """Makes a character register as Good."""

    def __init__(self, affected_player, source_player):
        super().__init__(affected_player, source_player)
        self._name = "Registers as Evil"

    # noinspection PyUnusedLocal
    @staticmethod
    def registers_evil(game: "Game"):
        """Determine whether the effect makes the player register as evil."""
        return True


class RegistersTownsfolk(Effect):
    """Makes a character register as a Townsfolk."""

    def __init__(self, affected_player, source_player):
        super().__init__(affected_player, source_player)
        self._name = "Registers as a Townsfolk"

    # noinspection PyUnusedLocal
    @staticmethod
    def registers_townsfolk(game: "Game"):
        """Determine whether the effect makes the player register as a townsfolk."""
        return True


class RegistersOutsider(Effect):
    """Makes a character register as a Outsider."""

    def __init__(self, affected_player, source_player):
        super().__init__(affected_player, source_player)
        self._name = "Registers as an Outsider"

    # noinspection PyUnusedLocal
    @staticmethod
    def registers_outsider(game: "Game"):
        """Determine whether the effect makes the player register as an outsider."""
        return True


class RegistersMinion(Effect):
    """Makes a character register as a Minion."""

    def __init__(self, affected_player, source_player):
        super().__init__(affected_player, source_player)
        self._name = "Registers as a Minion"

    # noinspection PyUnusedLocal
    @staticmethod
    def registers_minion(game: "Game"):
        """Determine whether the effect makes the player register as a minion."""
        return True


class RegistersDemon(Effect):
    """Makes a character register as a Demon."""

    def __init__(self, affected_player, source_player):
        super().__init__(affected_player, source_player)
        self._name = "Registers as a Demon"

    # noinspection PyUnusedLocal
    @staticmethod
    def registers_demon(game: "Game"):
        """Determine whether the effect makes the player register as a demon."""
        return True


# TODO: explore if __init_subclass__ is a way better method to do this
