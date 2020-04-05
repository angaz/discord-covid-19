import asyncio
from io import BytesIO

from matplotlib import pyplot as plt
from PIL import Image

from country_day_data import CountryData, CountryDataList


def axes_confirmed_since_nth_case(country: CountryData, since_nth_case: int):
    x, y = country.axes_confirmed()
    offset = [i >= since_nth_case for i in y].index(True)
    return offset, x, y


def _graph_since_nth_case(countries: CountryDataList, since_nth_case: int,) -> Image:
    countries = [
        (c, *axes_confirmed_since_nth_case(c, since_nth_case)) for c in countries
    ]
    first_country = countries[0]
    length = len(first_country[3]) - first_country[1]

    fig, ax = plt.subplots()

    for country, offset, x, y in countries:
        if offset == -1:
            continue

        off_len = offset + length
        y_plot = y[offset:off_len]
        ax.plot(
            range(len(y_plot)),
            y_plot,
            marker="o",
            label=(
                f"{country.country.name} ({offset} days offset)"
                if since_nth_case
                else country.country.name
            ),
        )

    ax.set_title(f"Confirmed Cases vs Time since {since_nth_case}th case")
    ax.set_xlabel(
        f"Days since {since_nth_case}th case ({length} days for {first_country[0].country.name})"
    )
    ax.set_ylabel("Number of cases")
    ax.legend()
    fig.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return buf


async def graph_since_nth_case(
    countries: CountryDataList, since_nth_case: int
) -> Image:
    return await asyncio.get_event_loop().run_in_executor(
        None, _graph_since_nth_case, countries, since_nth_case
    )
