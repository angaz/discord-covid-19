import typing
from datetime import datetime

from aiohttp import web

from country_day_data import filter_countries
from graphs import graph, graph_since_nth_case
from utils import axes_data

from .routes import routes


def graph_title(series: typing.Sequence[str]) -> str:
    out = {"deaths": "Deaths", "confirmed": "Confirmed Cases"}
    try:
        return ", ".join([out[s] for s in series])
    except KeyError as e:
        raise web.HTTPBadRequest(
            text=(
                f"{str(e)} is not a valid series.\n\n"
                "Valid series are none, one or both: 'confirmed' or 'deaths'.\n"
                "If left empty, 'confirmed' will be used."
            )
        )


@routes.get("/graph")
async def graph_endpoint(request: web.Request) -> web.Response:
    country_names = request.query.get("countries", "global").split(",")
    series = request.query.get("series", "confirmed").split(",")
    since_case = request.query.get("since")

    for key in request.query.keys():
        if key not in ("countries", "series", "since", "nonce"):
            raise web.HTTPBadRequest(
                text=(
                    f"'{key}' is not a valid parameter.\n"
                    "Valid parameters are none, one or many: 'countries', 'series', and 'since'.\n"
                    "You can add an optional 'nonce' as a cache invalidation method."
                )
            )

    if since_case is not None and not since_case.isnumeric():
        raise web.HTTPBadRequest(text=f"Since Case value is not numeric.")

    try:
        countries = filter_countries(request.app["data"], country_names)
    except LookupError as e:
        raise web.HTTPBadRequest(
            text=(
                f"{str(e)}.\n\n"
                "You can use none, one or many country codes or names.\n"
                "If left empty, 'global' will be used.\n"
                "Both Alpha-2 and Alpha-3 country codes will work.\n"
                "Prefer country codes to names.\n\n"
                "Special names: 'global', 'diamond_princess', and 'ms_zaandam'"
            )
        )

    image = (
        await graph(axes_data(countries, series), graph_title(series))
        if since_case is None
        else await graph_since_nth_case(
            axes_data(countries, series), graph_title(series), int(since_case)
        )
    )
    filename = "_".join(
        [
            datetime.utcnow().strftime("%Y%m%dT%H%M%S"),
            *[c.country.alpha_2.lower() for c in countries],
        ]
    )

    image_bytes = image.getvalue()
    return web.Response(
        body=image_bytes,
        headers={
            "Content-Disposition": (
                f'filename="{filename}.png"'
                if since_case is None
                else f'filename="{filename}_since_{since_case}.png"'
            ),
            "Content-Length": str(len(image_bytes)),
            "Content-Type": "image/png",
        },
    )
