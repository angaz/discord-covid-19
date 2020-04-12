import typing

from .validate_series import validate_series

SERIES_MAP = {"deaths": "Deaths", "confirmed": "Confirmed Cases"}


def graph_title(series: typing.Sequence[str]) -> str:
    validate_series(series)
    return ", ".join(SERIES_MAP[s] for s in series)
