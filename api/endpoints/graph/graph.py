from datetime import datetime

from aiohttp import web

from api.endpoints.utils import (
    graph_title,
    validate_query_keys,
    validate_scale,
    validate_since_case,
)
from country_day_data import filter_countries
from graphs import graph, graph_since_nth_case
from utils import axes_data

from .routes import routes


@routes.get("/graph")
async def graph_endpoint(request: web.Request) -> web.Response:
    country_names = request.query.get("countries", "global").split(",")
    series = request.query.get("series", "confirmed").split(",")
    since_case = request.query.get("since")
    scale = request.query.get("scale", "linear")

    validate_query_keys(request.query.keys())
    validate_scale(scale)
    validate_since_case(since_case)
    countries = filter_countries(request.app["data"], country_names)

    image = (
        await graph(axes_data(countries, series), graph_title(series), scale)
        if since_case is None
        else await graph_since_nth_case(
            axes_data(countries, series), graph_title(series), scale, int(since_case)
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
