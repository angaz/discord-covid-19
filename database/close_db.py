from aiohttp import web


async def close_database(app: web.Application) -> None:
    await app["pool"].close()
