import typing
from datetime import datetime

from aiohttp import web

from country_day_data import filter_countries
from graphs import graph, graph_since_nth_case
from utils import axes_data

from .routes import routes


def graph_title(series: typing.Sequence[str]) -> str:
    out = {"deaths": "Deaths", "confirmed": "Confirmed Cases"}
    return ", ".join([out[s] for s in series])


@routes.get("/graph")
async def graph_endpoint(request: web.Request) -> web.Response:
    country_names = request.query.get("countries", "global").split(",")
    series = request.query.get("series", "confirmed").split(",")
    since_case = request.query.get("since_case")

    try:
        countries = filter_countries(request.app["data"], country_names)
    except LookupError as e:
        raise web.HTTPBadRequest(text=str(e))

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
