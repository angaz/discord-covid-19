from aiohttp import web


def validate_scale(scale: str):
    if scale not in ("linear", "log"):
        raise web.HTTPBadRequest(
            text=(
                f"'{scale}' is not a valid scale value.\n\n"
                "Valid values are 'linear' or 'log.\n"
                "If left empty, 'linear' will be used."
            )
        )
