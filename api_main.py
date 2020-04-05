import logging

from aiohttp import web
from matplotlib import pyplot as plt

from api.endpoints.routes import add_routes
from utils import init_startup


async def init_app() -> web.Application:
    app = web.Application()
    logging.basicConfig(level=logging.INFO)

    add_routes(app)
    init_startup(app)

    return app


def main():
    plt.style.use("discord.mplstyle")
    web.run_app(
        init_app(),
        access_log_format='%a %t "%r" %s %b %Tf "%{Referer}i" "%{User-Agent}i"',
    )


if __name__ == "__main__":
    main()
