"""Contains the Vortox class."""

from lib.logic.Character import Demon


class Vortox(Demon):
    """The Vortox."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Vortox"
        self.playtest = False
