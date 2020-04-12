import typing

from aiohttp import web

SERIES_HELP = (
    "Valid series are none, one or both of 'confirmed' or 'deaths'.\n"
    "If left empty, 'confirmed' will be used."
)


def validate_series(series: typing.Sequence[str]):
    if len(series) > 2:
        raise web.HTTPBadRequest(
            text="Series has an invalid length. Max valid length is 2.\n\n"
            + SERIES_HELP
        )

    for s in series:
        if s not in ("deaths", "confirmed"):
            raise web.HTTPBadRequest(
                text=f"'{s}' not a valid series.\n\n" + SERIES_HELP
            )
