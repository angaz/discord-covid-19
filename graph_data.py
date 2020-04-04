import asyncio
from matplotlib import pyplot as plt
from graphs import graph, graph_since_nth_case
from sys import argv
from pathlib import Path
import pycountry
import typing

from aiohttp import ClientSession
from scraper import initialize_data
from country_day_data import CountryDataList


def country_to_identifier(search: str):
    pyc = pycountry.countries.search_fuzzy(search)
    return pyc[0].alpha_2.upper() if pyc else search.replace(" ", "_").upper()


def filter_countries(data: CountryDataList, country_names: typing.Sequence[str]):
    return [data[country_to_identifier(cn)] for cn in country_names]


async def _main():
    outdir = Path(argv[1]) if len(argv) > 1 else Path()

    async with ClientSession() as session:
        data = await initialize_data(session)

    plt.style.use("discord.mplstyle")

    cz_za_countries = filter_countries(data, ["CZ", "ZA"])
    us_za_countries = filter_countries(data, ["US", "ZA"])
    since_0_countries = filter_countries(data, ["ZA", "Italy", "KR", "CZ", "US"])

    cz_za_graph = graph(cz_za_countries)
    us_za_graph = graph(us_za_countries)
    since_0_graph = graph_since_nth_case(since_0_countries, 0)

    cz_za_graph.convert("RGB").save(outdir / "graph_cz_za.png")
    us_za_graph.convert("RGB").save(outdir / "graph_us_za.png")
    since_0_graph.convert("RGB").save(outdir / "graph_since_0.png")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(_main())
