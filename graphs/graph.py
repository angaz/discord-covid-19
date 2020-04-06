import asyncio
from io import BytesIO

import matplotlib.dates as mdates
from matplotlib import pyplot as plt

from country_day_data import CountryDataList


def _graph(countries: CountryDataList, title: str) -> BytesIO:
    fig, ax = plt.subplots()

    for country, label, (x, y) in countries:
        ax.plot(x, y, marker="o", label=label)
        ax.annotate(
            y[-1],
            xy=(1, y[-1]),
            xytext=(5, -5),
            xycoords=("axes fraction", "data"),
            textcoords="offset pixels",
        )

    locator = mdates.AutoDateLocator(minticks=3, maxticks=9)
    formatter = mdates.ConciseDateFormatter(locator, show_offset=False)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    ax.set_title(f"{title} vs Time")
    ax.set_xlabel("Date")
    ax.set_ylabel(f"Number of {title}")
    ax.legend()
    fig.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return buf


async def graph(countries: CountryDataList, title: str) -> BytesIO:
    return await asyncio.get_event_loop().run_in_executor(
        None, _graph, countries, title
    )
