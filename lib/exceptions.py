"""Contains custom exceptions."""


class _InvalidTargetError(Exception):
    """Invalid target selected."""

    default = None

    def __init__(self, **kwargs):
        self.out = kwargs.pop("out", self.default)


class InvalidMorningTargetError(_InvalidTargetError):
    """Invalid target selected during the morning."""

    default = [], []


class AlreadyNomniatedError(Exception):
    """The nominator already nominated."""

    pass


class PlayerNotFoundError(ValueError):
    """No matching player was found."""

    pass
