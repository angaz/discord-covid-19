import typing
import pycountry
import matplotlib.dates as mdates
from matplotlib import pyplot as plt
from pathlib import Path

from country_day_data import CountryDataList


def graph(
    data: CountryDataList, outdir: Path, country_names: typing.Sequence[str],
):
    country_codes = [
        pycountry.countries.search_fuzzy(cn)[0].alpha_2 for cn in country_names
    ]
    countries = [
        (c, *c.axes_confirmed())
        for c in data
        if (c.country and c.country.alpha_2 in country_codes)
        or c.country_region in country_names
    ]

    fig, ax = plt.subplots()

    for country, x, y in countries:
        ax.plot(x, y, marker="o", label=country.country.name)

    locator = mdates.AutoDateLocator(minticks=3, maxticks=9)
    formatter = mdates.ConciseDateFormatter(locator, show_offset=False)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    ax.set_xlabel("Date")
    ax.set_ylabel("Number of cases")
    ax.legend()
    fig.tight_layout()
    fig.savefig(outdir / "graph.png")
