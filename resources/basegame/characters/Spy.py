"""Contains the Spy class."""

from typing import TYPE_CHECKING

from lib.logic.Character import Minion

if TYPE_CHECKING:
    from lib.typings.context import Context


class Spy(Minion):
    """The Spy."""

    name: str = "Spy"
    playtest: bool = False

    async def morning_call(self, ctx: "Context") -> str:
        """Determine the morning call."""
        return (
            "Show the spy the grimoire. "
            f"(You may view the grimoire with `{ctx.prefix}grimoire'.)"
        )
