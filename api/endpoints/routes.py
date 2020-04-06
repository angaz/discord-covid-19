from aiohttp import web

from .graph import graph_routes
from .update_data import update_data_routes

route_tables = (
    graph_routes,
    update_data_routes,
)


def add_routes(app: web.Application):
    for route_table in route_tables:
        app.add_routes(route_table)
