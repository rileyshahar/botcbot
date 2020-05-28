"""Contains the Chef class."""

from typing import TYPE_CHECKING

from lib.logic.Character import Townsfolk
from lib.logic.charcreation import if_functioning

if TYPE_CHECKING:
    from lib.typings.context import Context


class Chef(Townsfolk):
    """The Chef."""

    name: str = "Chef"
    playtest: bool = False

    @if_functioning(True)
    async def morning_call(
        self, ctx: "Context", enabled=True, epithet_string=""
    ) -> str:
        """Determine the morning call."""
        numb = 0
        for character in ctx.bot.game.seating_order:
            if character.is_status(ctx.bot.game, "evil", registers=True):
                if character.neighbors(ctx.bot.game)[1].is_status(
                    ctx.bot.game, "evil", registers=True
                ):
                    numb += 1
        out = (
            f"Tell {self.parent.formatted_epithet(epithet_string)}, "
            "the number of evil pairs "
        )
        if enabled:
            out += f"(**{numb}**)."
        else:
            out += "(this may be any number)."
        return out
