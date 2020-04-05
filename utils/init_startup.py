from aiohttp import web

from .update_data import update_data


def init_startup(app: web.Application):
    app.on_startup.extend([update_data])
