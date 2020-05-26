"""Contains custom exceptions."""

from typing import Any, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from lib.logic.Player import Player


class _InvalidTargetError(Exception):
    """Invalid target selected."""

    default: Any = None

    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.out = kwargs.pop("out", self.default)


class InvalidMorningTargetError(_InvalidTargetError):
    """Invalid target selected during the morning."""

    default: Tuple[List["Player"], List[str]] = [], []


class AlreadyNomniatedError(Exception):
    """The nominator already nominated."""


class PlayerNotFoundError(ValueError):
    """No matching player was found."""
