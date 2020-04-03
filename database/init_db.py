import json

import asyncpg  # type: ignore
from aiohttp import web

from config import config


async def init_pool(app: web.Application) -> None:
    app["pool"] = await asyncpg.create_pool(**config["database"])
