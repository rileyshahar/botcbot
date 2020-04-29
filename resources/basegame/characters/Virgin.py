"""Contains the Virgin class."""

from lib.logic.Character import Townsfolk
from lib.logic.Day import generate_nomination_message_text
from lib.logic.Effect import UsedAbility
from lib.logic.tools import if_functioning, onetime_use
from lib.utils import safe_send


class Virgin(Townsfolk):
    """The Virgin."""

    name: str = "Virgin"
    playtest: bool = False

    @if_functioning(True)
    @onetime_use
    async def nomination(
        self, ctx, nominee, nominator, enabled=True, epithet_string=""
    ):
        """Handle Virgin nomination.

        If nominee is the Virgin and nominator is a townsfolk, execute nominator.
        """
        if nominee == self.parent:
            self.parent.add_effect(ctx, UsedAbility, self.parent)
            if enabled and nominator.is_status(ctx, "townsfolk", registers=True):
                await safe_send(
                    ctx.bot.channel,
                    generate_nomination_message_text(
                        ctx, nominator, nominee, traveler=False, proceed=False
                    ),
                )
                await nominator.execute(ctx)
                return False
        return True
