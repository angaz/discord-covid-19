from aiohttp import web

from utils.update_data import update_data

from .routes import routes


@routes.get("/update_data")
async def update_data_handler(request: web.Request) -> web.Response:
    await update_data(request.app)
    return web.Response()
