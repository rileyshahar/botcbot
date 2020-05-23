"""Contains the Empath class."""

from lib.logic.Character import Townsfolk
from lib.logic.charcreation import if_functioning
from lib.typings.context import Context


class Empath(Townsfolk):
    """The Empath."""

    name: str = "Empath"
    playtest: bool = False

    @if_functioning(True)
    async def morning_call(self, ctx: Context, enabled=True, epithet_string="") -> str:
        """Determine the morning call."""
        neighbors = self.parent.neighbors(
            ctx.bot.game, condition=lambda x, y: not x.ghost(y, registers=True)
        )
        numb = len(
            [
                player
                for player in neighbors
                if player and player.is_status(ctx.bot.game, "evil", registers=True)
            ]
        )
        out = (
            f"Tell {self.parent.formatted_epithet(epithet_string)}, "
            "a number of evil living neighbors "
        )
        if enabled:
            out += f"(**{numb}**)."
        else:
            out += "(this may be any number)."
        return out
