"""Contains the FangGu class."""

from lib.logic.Character import Demon


class FangGu(Demon):
    """The Fang Gu."""

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Fang Gu"
        self.playtest = False
