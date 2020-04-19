import typing

from aiohttp import web


def validate_query_keys(query_keys: typing.Sequence[str]):
    for key in query_keys:
        if key not in ("countries", "scale", "series", "since", "nonce"):
            raise web.HTTPBadRequest(
                text=(
                    f"'{key}' is not a valid parameter.\n"
                    "Valid parameters are none, one or many: 'countries', 'scale', 'series', and 'since'.\n"
                    "You can add an optional 'nonce' as a cache invalidation method."
                )
            )
