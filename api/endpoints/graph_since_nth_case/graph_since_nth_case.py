from datetime import datetime

from aiohttp import web

from country_day_data import filter_countries
from graphs import graph_since_nth_case

from .routes import routes


@routes.get("/graph_since_case")
async def graph_since_nth_case_endpoint(request: web.Request) -> web.Response:
    country_names = request.rel_url.query.get("countries", "global").split(",")
    since_case = int(request.rel_url.query.get("since_case", "0"))

    try:
        countries = filter_countries(request.app["data"], country_names)
    except LookupError as e:
        raise web.HTTPBadRequest(text=str(e))

    image = await graph_since_nth_case(countries, since_case)
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
            "Content-Disposition": f'filename="{filename}_since_{since_case}.png"',
            "Content-Length": str(len(image_bytes)),
            "Content-Type": "image/png",
        },
    )
