import asyncio
from matplotlib import pyplot as plt
from graphs import graph, graph_since_nth_case
from sys import argv
from pathlib import Path

from aiohttp import ClientSession
from scraper import initialize_data


async def _main():
    outdir = Path(argv[1]) if len(argv) > 1 else Path()

    async with ClientSession() as session:
        data = await initialize_data(session)

    plt.style.use("discord.mplstyle")

    graph(data, outdir, ["Czech Republic", "South Africa"])
    graph_since_nth_case(
        data, outdir, ["South Africa", "Italy", "KR", "Czech Republic"], 0
    )


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(_main())