"""Contains custom exceptions."""


class _InvalidTarget(Exception):
    """Invalid target selected."""

    default = None

    def __init__(self, **kwargs):
        self.out = kwargs.pop("out", self.default)


class InvalidMorningTarget(_InvalidTarget):
    """Invalid target selected during the morning."""

    default = [], []


class AlreadyNomniatedError(Exception):
    """The nominator already nominated."""

    pass


class PlayerNotFoundError(ValueError):
    """No matching player was found."""

    pass
