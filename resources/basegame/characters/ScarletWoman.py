"""Contains the ScarletWoman class."""

from lib.logic.Character import Minion


class ScarletWoman(Minion):
    """The Scarlet Woman."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Scarlet Woman"
        self.playtest = False
