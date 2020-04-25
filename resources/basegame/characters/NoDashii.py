"""Contains the NoDashii class."""

from lib.logic.Character import Demon


class NoDashii(Demon):
    """The No Dashii."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "No Dashii"
        self.playtest = False
