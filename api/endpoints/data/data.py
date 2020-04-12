from aiohttp import web

from api.endpoints.utils import graph_title, validate_query_keys, validate_since_case
from country_day_data import filter_countries
from utils import axes_data

from .routes import routes


@routes.get("/data")
async def data_endpoint(request: web.Request) -> web.Response:
    country_names = request.query.get("countries", "global").split(",")
    series = request.query.get("series", "confirmed").split(",")
    since_case = request.query.get("since")

    validate_query_keys(request.query.keys())
    validate_since_case(since_case)
    countries = [
        {"country": country.to_dict_without_days(), "label": label, "axes": axes}
        for country, label, axes in axes_data(
            filter_countries(request.app["data"], country_names)
        )
    ]

    return web.json_response({"title": graph_title(series), "countries": countries})
