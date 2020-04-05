from datetime import datetime

from aiohttp import web

from country_day_data import filter_countries
from graphs import graph

from .routes import routes


@routes.get("/graph")
async def graph_endpoint(request: web.Request) -> web.Response:
    country_names = request.rel_url.query.get("countries", "global").split(",")

    try:
        countries = filter_countries(request.app["data"], country_names)
    except LookupError as e:
        raise web.HTTPBadRequest(text=str(e))

    image = await graph(countries)
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
            "Content-Disposition": f'filename="{filename}.png"',
            "Content-Length": str(len(image_bytes)),
            "Content-Type": "image/png",
        },
    )
