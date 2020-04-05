import asyncio
from io import BytesIO

import matplotlib.dates as mdates
from matplotlib import pyplot as plt
from PIL import Image

from country_day_data import CountryDataList


def _graph(countries: CountryDataList) -> BytesIO:
    countries = [(c, *c.axes_confirmed()) for c in countries]

    fig, ax = plt.subplots()

    for country, x, y in countries:
        ax.plot(x, y, marker="o", label=country.country.name)

    locator = mdates.AutoDateLocator(minticks=3, maxticks=9)
    formatter = mdates.ConciseDateFormatter(locator, show_offset=False)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    ax.set_title("Confirmed Cases vs Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Number of Confirmed Cases")
    ax.legend()
    fig.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return buf


async def graph(countries: CountryDataList) -> Image:
    return await asyncio.get_event_loop().run_in_executor(None, _graph, countries)
