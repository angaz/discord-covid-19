from aiohttp import ClientSession, web

from scraper import initialize_data


async def update_data(app: web.Application):
    async with ClientSession() as session:
        data = await initialize_data(session)

    app["data"] = data
