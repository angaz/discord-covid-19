from aiohttp import web


def validate_since_case(since_case: str):
    if since_case is not None and not since_case.isnumeric():
        raise web.HTTPBadRequest(text=f"Since Case value is not numeric.")
