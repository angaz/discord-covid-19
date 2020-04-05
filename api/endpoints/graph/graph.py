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
        [*[c.country.alpha_2.lower() for c in countries], datetime.utcnow().isoformat()]
    )

    return web.Response(
        body=image.getvalue(),
        headers={
            "Content-Type": "image/png",
            "Content-Disposition": f'filename="{filename}.png"',
        },
    )
