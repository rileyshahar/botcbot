"""Contains abstract base classes for game logic handling."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Tuple

from lib.typings.context import Context

if TYPE_CHECKING:
    from lib.logic.Player import Player


class NightOrderMember(ABC):
    """An ABC detailing requirements for an object to be in the night order."""

    @abstractmethod
    async def morning_call(self, ctx: Context) -> str:
        """Get the text to display when first called in the morning."""
        raise NotImplementedError

    # pylint: disable=unused-argument
    async def morning(self, ctx: Context) -> Tuple[List["Player"], List[str]]:
        """Call in the morning."""
        return [], []
